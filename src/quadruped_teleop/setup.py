from setuptools import find_packages, setup

package_name = 'quadruped_teleop'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'flask', 'opencv-python', 'cv-bridge'],
    zip_safe=True,
    maintainer='rcardenas',
    maintainer_email='rhandycardenasc@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'quadruped_teleop = quadruped_teleop.teleop_node:main',
        ],
    },
)
