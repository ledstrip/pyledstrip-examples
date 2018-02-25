import pygst

pygst.require('0.10')
import gst, gobject

gobject.threads_init()

pipeline_play = None
pipeline = gst.parse_launch(
    'pulsesrc ! audioconvert ! '
    'audio/x-raw-int,channels=2,rate=44100,endianness=1234,'
    'width=32,depth=32,signed=(bool)True !'
    'level name=level interval=10000000 !'
    'appsink name=app emit-signals=True')

state = 'wait'
peak = -99
buffers = []
level = pipeline.get_by_name('level')
app = pipeline.get_by_name('app')
bus = pipeline.get_bus()
bus.add_signal_watch()


def show_peak(bus, message):
    global peak
    # filter only on level messages
    if message.src is not level:
        return
    if not message.structure.has_key('peak'):
        return
    # read peak
    peak = message.structure['peak'][0]


def enqueue_audio_buffer(app):
    buffers.append(str(app.emit('pull-buffer')))


def play_sample(sample):
    global pipeline_play
    with open('audio.dat', 'wb') as fd:
        fd.write(sample)
    if pipeline_play is None:
        pipeline_play = gst.parse_launch(
            'filesrc location=audio.dat !'
            'audio/x-raw-int,channels=2,rate=44100,endianness=1234,'
            'width=32,depth=32,signed=(bool)True !'
            'audioamplify amplification=2 ! autoaudiosink')
    pipeline_play.set_state(gst.STATE_NULL)
    pipeline_play.set_state(gst.STATE_PLAYING)


# connect the callback
bus.connect('message', show_peak)
app.connect('new-buffer', enqueue_audio_buffer)

# start the pipeline
pipeline.set_state(gst.STATE_PLAYING)

# main loop
ctx = gobject.gobject.main_context_default()
while ctx:
    ctx.iteration()
    print
    state, peak

    # wait for somebody to make a sound
    if state == 'wait':
        if peak > -30:
            state = 'record'
            continue
        # discard any buffer
        buffers = []

    # record the current audio, until the peak is going down
    elif state == 'record':
        if peak < -32:
            state = 'replay'
            continue

    # replay last sound
    elif state == 'replay':
        play_sample(''.join(buffers))
        state = 'wait'