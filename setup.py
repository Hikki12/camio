from distutils.core import setup


setup(
      name='camio',
      version='0.1',
      description='Python camIO',
      author='Jason Macas',
      author_email='franciscomacas3@gmail.com',
      install_requires=[i.strip() for i in open("./requirements.txt").readlines()]
)
