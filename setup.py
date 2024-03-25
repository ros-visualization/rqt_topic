from setuptools import setup

package_name = "rqt_topic"
setup(
    name=package_name,
    version='1.7.1',
    package_dir={'': '.'},
    packages=[
        package_name,
        f'{package_name}/models',
        f'{package_name}/buttons',
        f'{package_name}/views',
        f'{package_name}/workers',
    ],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name + '/resource', ['resource/TopicWidget.ui']),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['plugin.xml']),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    author="Dorian Scholz",
    maintainer="Brandon Ong",
    maintainer_email="brandon@openrobotics.org",
    keywords=["ROS"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    description=(
        "rqt_topic provides a GUI plugin for displaying debug information about ROS topics "
        "including publishers, subscribers, publishing rate, and ROS Messages."
    ),
    license="BSD",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "rqt_topic = " + package_name + ".main:main",
        ],
    },
)
