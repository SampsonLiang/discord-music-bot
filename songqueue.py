queues = {}
titles = {}
current_songs = {}

def play_next(ctx, id):
    '''
    Plays the next song in queue.
    '''
    if queues[id]:
        if len(queues[id]) >= 1:
            voice = ctx.voice_client
            source = queues[id].pop(0)

            title = titles[id].pop(0)
            current_songs[id] = title

            voice.play(source, after = lambda x: play_next(ctx, id))