from setuptools import find_packages, setup

package_name = 'my_robot_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mahdi Yousef',
    maintainer_email='you@example.com',
    description='Custom autonomy nodes for the TurtleBot3-based project.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'obstacle_avoider = my_robot_control.obstacle_avoider:main',
            'waypoint_follower = my_robot_control.waypoint_follower:main',
        ],
    },
)
