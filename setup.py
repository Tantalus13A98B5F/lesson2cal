from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
options = {
    'build_exe': {
        'packages': [
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
        ],
        'excludes': ['tkinter'],
        'include_files': [
            'templates',
            'static'
        ],
    }
}

executables = [
    Executable('server.py', base='Console', targetName='lesson2cal.exe')
]

setup(name='lesson2cal',
    version='2019.9.7',
    description='',
    options=options,
    executables=executables)
