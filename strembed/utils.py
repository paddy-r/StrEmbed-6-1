from . import embed_images, occ_patch_manual

def do_fixes():
    # Block for embed_images to ensure all images and icons are embedded in script
    try:
        print('\n## Trying to embed images... ##\n')
        embed_images.embed()
        print('\n## Done embedding images ##\n')
    except:
        print('\## Could not embed images; exception follows')
        print(e)
        print('\n## If you see this error while running an executable of StrEmbed, please run "embed_images" in a Python terminal then create a new executable ##\n')


    # Block for occ_manual_patch to fix OCC classes
    try:
        print('\n## Trying to manually patch OCC classes to allow deep-copying for assembly duplication etc... ##\n')
        occ_patch_manual.patch()
        print('\n## Done OCC patch ##\n')
    except:
        print('\## Could not complete OCC patch; exception follows')
        print(e)
        print('\n## If you see this error while running an executable of StrEmbed, please run "occ_patch_manual" in a Python terminal then create a new executable ##\n')