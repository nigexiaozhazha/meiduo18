from rest_framework import serializers
from users.models import User
from django_redis import get_redis_connection

import re


class UserSerilizer(serializers.ModelSerializer):
    # 显示指明字段
    password2 = serializers.CharField(max_length=20, min_length=8, write_only=True)
    sms_code = serializers.CharField(max_length=6, min_length=6, write_only=True)
    allow = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password', 'password2', 'sms_code', 'allow')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
                'error_messages': {
                    'max_length': '密码过长'
                }
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
                'error_messages': {
                    'max_length': '名字过长'
                }
            },
        }

    # 手机号验证
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机格式不正确')

        return value

    # 验证协议状态
    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('协议未选中')

        return value

    # 多个字段验证
    def validate(self, attrs):
        # 密码检验
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('密码不一致')

        # 短信验证码验证
        # 建立redis连接
        conn = get_redis_connection('verify')
        # 取出真实验证码 bytes类型
        real_sms = conn.get('sms_%s' % attrs['mobile'])
        # 判断是否能取出值
        if not real_sms:
            return serializers.ValidationError('验证码已过期')

        # 验证码校验
        if attrs['sms_code'] != real_sms.decode():
            raise serializers.ValidationError('短信验证码不一致')
        return attrs

    # 上面的业务逻辑通过验证后,需要进行保存操作时会报错,因为数据库没有指明字段
    # 所以需要重写create 方法
    def create(self, validated_data):
        # 删除验证后的指明字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        print(validated_data)

        # 1.继承父类方法,再进行保存,密码自动加密
        # user = super().create(validated_data)

        # 2.密码自动加密
        user = User.objects.create_user(username=validated_data['username'], mobile=validated_data['mobile'], password=validated_data['password'])

        # 3.密码需要手动加密
        # user = User.objects.create(username=validated_data['username'])
        # user.set_password(validated_data['password'])
        # user.save()

        return user
