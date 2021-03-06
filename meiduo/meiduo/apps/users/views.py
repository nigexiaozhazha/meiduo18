from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from rest_framework.response import Response
from meiduo.libs.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code
from users.models import User
# Create your views here.


# 短信验证码
from users.serializers import UserSerilizer


class SMSCodeView(APIView):
    def get(self, request, mobile):
        # 建立连接,得到连接对象
        # 判断发送频率 控制再60s内不许再次发送
        conn = get_redis_connection('verify')
        flag = conn.get('sms_flag_%s' % mobile)
        if flag:
            return Response({'errors': '请求过于频繁'}, status=402)
        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        print('短信验证码为[%s]'% sms_code)
        # 保存短信验证码
        pl = conn.pipeline()
        pl.setex('sms_%s' % mobile, 300, sms_code)
        pl.setex('sms_flag_%s' % mobile, 60, 'zhazha')

        pl.execute()  # 传入指令,会执行写入redis命令
        # 发送短信验证码
        # 通过celery发送短信
        send_sms_code.delay(mobile, sms_code)
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, '5'], 1)

        # json 返回数据
        return Response({'message': 'OK'})

# 判断用户名是否存在
class UserNameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return Response(
            {
                'count': count
            }
        )

# 判断手机号是否存在
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return Response(
            {
                'count': count
            }
        )

# 实现注册业务
class UserView(CreateAPIView):
    serializer_class = UserSerilizer
