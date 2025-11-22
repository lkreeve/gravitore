setup(
    name="gravitore",
    version="1.0.0",
    description="Read the latest Real Python tutorials",
    long_description=README.md,
    long_description_content_type="text/markdown",
    url="https://github.com/realpython/reader",
    author="Real Python",
    author_email="info@realpython.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=['gravitore'],
    package_dir={'gravitore': 'gravitore'},
    package_data={'gravitore': ['gravitore/assets.pyxres']}
    include_package_data=True,
    install_requires=[
        "pyxel"
    ],
)