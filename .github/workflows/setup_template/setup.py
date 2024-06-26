import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
try:
    # pip >=20
    from pip._internal.network.session import PipSession
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        # 10.0.0 <= pip <= 19.3.1
        from pip._internal.download import PipSession
        from pip._internal.req import parse_requirements
    except ImportError:
        # pip <= 9.0.3
        from pip.download import PipSession
        from pip.req import parse_requirements

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

e2eaiok_home = os.path.join(os.path.dirname(os.path.abspath(__file__)), "e2eAIOK")
VERSION = open(os.path.join(e2eaiok_home, "version"), 'r').read().strip()

def setup_package(args):
    metadata = dict(
        name=args["name"],
        version=VERSION,
        author="INTEL",
        license='Apache License',
        description="Intel® End-to-End AI Optimization Kit",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/intel/e2eAIOK",
        project_urls={
            "Bug Tracker": "https://github.com/intel/e2eAIOK/issues",
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
        ],
        packages=args["packages"],
        package_data = args["package_data"],
        python_requires=">=3.6",
        zip_safe=False,
        cmdclass=args.get("cmdclass", {}),
        install_requires=args["install_requires"]
    )
    setup(**metadata)

class post_install_ma(install):
    def run(self):
        install.run(self)
        import os
        print(f"################### pip install tllib==0.4 ###################")
        os.system(f"pip install git+https://github.com/thuml/Transfer-Learning-Library.git")

if __name__ == '__main__':
    args = dict()

    args["name"] = "e2eAIOK-ModelAdapter"
    args["packages"] = find_packages(exclude=["RecDP", "RecDP.*", "modelzoo", "example", \
                                            "e2eAIOK.SDA", "e2eAIOK.SDA.*", "e2eAIOK.dataloader", "e2eAIOK.utils",\
                                            "e2eAIOK.DeNas", "e2eAIOK.DeNas.*"])
    args["package_data"] = {'e2eAIOK': ['version','common/default.conf','ModelAdapter/default_ma.conf', 'ModelAdapter/requirements.txt']}
    args['cmdclass'] = {'install': post_install_ma}
    install_reqs = parse_requirements("e2eAIOK/ModelAdapter/requirements.txt", session=False)
    # handle pip version compatibility
    try:
        args["install_requires"] = [str(ir.req) for ir in install_reqs]
    except AttributeError:
        args["install_requires"] = [str(ir.requirement) for ir in install_reqs]

    setup_package(args)