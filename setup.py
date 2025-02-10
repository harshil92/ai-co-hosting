from setuptools import setup, find_packages

setup(
    name="ai-co-host",
    version="0.1.0",
    description="AI Co-host Twitch Bot",
    author="AI Co-host Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "twitchio==2.8.2",
        "pydantic==2.5.3",
        "pydantic-settings==2.1.0",
        "websockets==12.0",
        "requests==2.31.0"
    ],
    entry_points={
        "console_scripts": [
            "ai-co-host=twitch_bot.__main__:main",
        ],
    },
) 