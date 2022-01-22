#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-pobretv.jarbasai=skill_pobretv:PobreTVSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-pobretv',
    version='0.0.1',
    description='ovos PobreTV skill plugin',
    url='https://github.com/JarbasSkills/skill-pobretv',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_pobretv": ""},
    package_data={'skill_pobretv': ['locale/*', 'ui/*']},
    packages=['skill_pobretv'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a1", "beautifulsoup4"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
