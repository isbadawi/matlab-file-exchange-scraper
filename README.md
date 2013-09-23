This is a script that downloads code from the [MatlabCentral File Exchange][mcfe].

You can use it like this:

```bash
$ python scrape.py --to=downloads/ --num_projects=10 --sort=downloads_desc
Downloading 23629-exportfig... done.
Downloading 32374-matlab-support-package-for-arduino-aka-arduinoio-package... done.
Downloading 22022-matlab2tikz... done.
Downloading 24861-41-complete-gui-examples... done.
Downloading 278-arrow-m... done.
Downloading 40876-android-sensor-support-from-matlab... done.
Downloading 18169-optical-character-recognition-ocr... done.
Downloading 8797-tools-for-nifti-and-analyze-image... done.
Downloading 7506-particle-swarm-optimization-toolbox... done.
Downloading 7401-scalable-vector-graphics-svg-export-of-figures... done.
```

The projects are downloaded to the directory specified by the `--to` flag, together
with a `manifest.json` file that describes them.

[mcfe]: http://www.mathworks.com/matlabcentral/fileexchange
