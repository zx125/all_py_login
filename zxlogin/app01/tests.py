from django.test import TestCase

# Create your tests here.
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zxlogin.settings")
    import django
    django.setup()
    from app01 import models
    from django.db.models import Count

    # article_list = models.Article.objects.all().first()
    # print(article_list)
    # print(article_list.blog)
    # res = models.Article.objects.annotate('desc').values_list('co')
    # print(res)
    # res = models.Article.objects.all()
    # for i in res:
    #     print(i)
    # print(res)
    # print(res)

    # for i in res:
    #     print(i.title)
    # for i in res:
    #     print(i.desc)

    # print(res)
    # print(res)
    category_list = models.Category.objects.filter(blog_id=2).all()
    print(category_list)