info_join = '**!join** - Invite the bot to VC\n'
info_leave = '**!leave** - Remove the bot from the VC\n'
info_play = '**!play** - Search for and play a song, or add it to queue\n'
info_playnow = '**!playnow** - Search for and play a song immediately\n'
info_pause = '**!pause** - Pause the current song\n'
info_resume = '**!resume** - Resume the current song\n'
info_skip = '**!skip** - Skip the current song\n'
info_skipto = '**!skipto** x - Skip to the song in position x in queue\n'
info_song = '**!song** - Get the name and artist of the current song\n'
info_queue = '**!queue** - Display all songs currently in queue\n'
info_remove = '**!remove** x - Remove the song in position x from the queue\n'
info_clear = '**!clear** - Remove all songs from the queue\n'

info_menu = [info_join, info_leave, info_play, info_playnow, info_pause, info_resume, info_skip, 
            info_skipto, info_song, info_queue, info_remove, info_clear]

def get_info():
    msg = ''
    for desc in info_menu:
        msg += desc
    return msg