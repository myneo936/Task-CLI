from setuptools import setup, find_packages

setup(
    name="task-cli",
    version="0.1.0",
    description="A command-line task scheduler",
    author="Sanskar",
    author_email="vatsalsanskar@gmail.com",
    url="https://github.com/myneo936/Task-CLI",
    packages=find_packages(),
    install_requires=[    
        "tabulate>=0.9.0",
    ],
    py_modules=["task_cli"],
    entry_points={
        'console_scripts': [
            'task_cli=task_cli:main',
        ],
    },
    python_requires='>=3.6',
)