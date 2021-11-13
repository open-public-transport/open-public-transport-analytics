
# HowTo analyse_gtfs.py 

Import ... source file must be an compatible GTFS zip file
Before you run the Example .. 

run ->
```bash
python .\analyse_gtfs.py --helpshort
```

## Examples

Example 1 ->
```bash
python .\analyse_gtfs.py --buckets 24 --source_file 'data/HVV-Soll-Fahrplandaten.zip' --dest_dir 'testdest/'
```

Example 2 ->
```bash
python .\analyse_gtfs.py --buckets 2 --source_file 'data/HVV-Soll-Fahrplandaten.zip' --dest_dir 'testdest/'
```
Calculate in 2 Hour Buckets ... you recieve Buckets in the window size ... 0-2, 2-4, 4-6, 6-8 ... 22-24 