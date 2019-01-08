from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
packages = [
    'asyncio.compat',
    'asyncio.constants',
    'asyncio.base_futures',
    'asyncio.base_tasks',
    'asyncio.base_subprocess',
    'asyncio.proactor_events',
    'asyncio.selector_events',
    'asyncio.windows_utils',
    'idna.idnadata',
    'jinja2.ext',
]
buildOptions = dict(packages=packages, excludes=[])

base = 'Console'

executables = [
    Executable('server.py', base=base, targetName='lesson2cal.exe')
]

setup(name='lesson2cal',
    version='2019.1.8',
    description='',
    options=dict(build_exe=buildOptions),
    executables=executables)
