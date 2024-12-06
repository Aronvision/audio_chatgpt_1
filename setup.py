from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'audio_chatgpt'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),  # 패키지 인덱스 마커 파일 설치
        ('share/' + package_name, ['package.xml']),  # package.xml 설치
        # 실행 파일을 설치합니다.
        (os.path.join('lib', package_name), glob('scripts/*')),
    ],
    install_requires=[
        'setuptools',
        'openai',
        'rclpy',
        'std_msgs',
    ],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='STT 결과를 ChatGPT로 보내는 ROS 2 노드',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'audio_chatgpt_node = audio_chatgpt.audio_chatgpt_node:main',
        ],
    },
)
