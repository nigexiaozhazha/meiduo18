from django.shortcuts import render
from rest_framework.views import APIView
from random import randint
from django_redis import get_redis_connection
from rest_framework.response import Response
from meiduo.libs.yuntongxun.sms import CCP


# Create your views here.
class SMSCodeView(APIView):
    def get(self, request, mobile):
        # 生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        # 保存短信验证码
        conn = get_redis_connection('verify')
        conn.setex('sms_%s' % mobile, 300, sms_code)
        # 发送短信验证码
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, '5'], 1)
        # json 返回数据
        return Response({'message': 'OK'})
