from plumbum import local

root = local.path('Audio Bible AB2013')


def clean_my_files(directory):
    contents = directory.iterdir()

    for content in contents:
        content = local.path(content)
        if content.isfile():
            name = content.basename
            renamed = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('|_', '')
            content.rename(renamed)


contents = root.iterdir()
for content in contents:
    clean_my_files(content)
    print("Done: {}".format(content))
