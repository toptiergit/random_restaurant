from setuptools import setup

setup(
    name="random_restaurant",
    version="1.0",
    description="โปรแกรมสุ่มร้านอาหาร",
    author="BBank",
    packages=["random_restaurant"],
    install_requires=[
        "tkinter",
    ],
    entry_points={
        'console_scripts': [
            'random-restaurant=random_restaurant:main',
        ],
    },
) 