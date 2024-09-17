import vlm
import oss2
# -*- coding: utf-8 -*-
from oss2.credentials import EnvironmentVariableCredentialsProvider

# 从config.py中获取访问凭证
auth = oss2.Auth(config.OSS_ACCESS_KEY_ID, config.OSS_ACCESS_KEY_SECRET)

# 填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
# yourBucketName填写存储空间名称。oss-cn-beijing-internal.aliyuncs.com
bucket = oss2.Bucket(auth, 'https://oss-cn-hangzhou.aliyuncs.com', 'lampbucket')

# 设置存储空间为私有读写权限。
bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)  
