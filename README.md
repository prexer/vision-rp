# vision-rp
This is my homegrown coding project to work with a Raspberry Pi and a camera, and make a motion-detecting camera.
This currently runs on a RasbperryPi3 with the standard (5MP) camera. 

I've pulled together various things from other people's blog posts, including some OpenCV 3. Most of it comes from the http://PyImageSearch.com site, but I've also added a bit of multithreading and done a bit of OO to bits of it. 

Anyone interested in contributing, let me know, and I'll be happy to chat with you. Producing a RPi image with OpenCV3 already installed would be a great boost forward for making more of these cameras without hours of installation work.

## How to install on your Raspberry PI

From your Raspberry pi, run the following:

```git clone https://github.com/prexer/vision-rp.git```

Then make a copy of the config.json.base and make it your own

```
cd vision-rp
cp config.json.base config.json
```

Then you'll need a dropbox account that you can logon to. You'll want to point your camera at something you want to watch for motion... and then you'll be ready to run the motion-detection system

To start it:

```$ python key_event_writer.py --conf conf.json```

For more info on where this all started from, see the pyvision article: http://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/







