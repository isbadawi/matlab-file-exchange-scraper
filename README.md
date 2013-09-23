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
with a `manifest.json` file that describes them. The manifest is an object with
a key `"projects"`, whose value is an array of objects that look like this:

```
{
  "author": "Juerg Schwizer", 
  "author_url": "http://www.mathworks.com/matlabcentral/fileexchange/authors/8708", 
  "date_submitted": "10 Apr 2005", 
  "date_updated": "17 Sep 2012", 
  "name": "7401-scalable-vector-graphics-svg-export-of-figures", 
  "summary": "Converts 3D and 2D MATLAB plots to the scalable vector format (SVG).", 
  "tags": [
    "3d", 
    "animation", 
    "blur", 
    "converter", 
    "data export", 
    "figure", 
    "graphics", 
    "image processing", 
    "light", 
    "plot2svg", 
    "plotting", 
    "scalable", 
    "shade", 
    "shadow", 
    "specialized", 
    "svg", 
    "svg filters", 
    "vector"
  ], 
  "title": "Scalable Vector Graphics (SVG) Export of Figures", 
  "url": "http://www.mathworks.com/matlabcentral/fileexchange/7401-scalable-vector-graphics-svg-export-of-figures"
} 
```

[mcfe]: http://www.mathworks.com/matlabcentral/fileexchange
