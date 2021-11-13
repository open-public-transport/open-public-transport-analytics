"""
Author:     Michael Schwabe
Version:    V0.5

Function:   Calculate GTFS Files from PublicTransport Agency/Company to SHape and GeoJSONs. 
            - Speed (max, avg and so on)
            - Frequenc (Stops, Segments, Lines)
"""

from absl import app, flags, logging
import gtfs_functions as gtfs
import numpy as np
def createList(r1, r2):
    return 

flags.DEFINE_integer('logging_level',
                     default=None, help='Integer parameter specifying the verbosity of the absl logging library')
flags.DEFINE_string('source_file',
                    default='', help='String parameter specifying the file path to the data file used for GTFS Source' 
                                       'from PublicTransport Data like a zip with some Data store in txt files .. (Stops, Lines etc pp.)'
                                       )
flags.DEFINE_string('dest_dir',
                    default='', help='Where do you save all the Stuff .. Default ist current working directory! .. select DIR+/ .. example data/')
flags.DEFINE_integer('buckets',
                     default=1, help='Integer parameter specifying the bucket size for calculation in hours. Must 24 % VALUE = 0 -> [1,2,3,4,6,8,12,24] ')
#flags.DEFINE_float('max_fitness',
#                   default=None, help='Float parameter specifying the fitness of the best genome at which point the '
#                                      'evolutionary process should preemptively end')

flags.register_validator('buckets',
                         lambda value: 24 % value == 0,
                         message='--cuttoff must be 24 modulo VALUE = 0 -> [1,2,3,4,6,8,12,24]')
flags.mark_flag_as_required('source_file')
#flags.mark_flag_as_required('buckets')


def calculation(_):
    """
    This Example evolves a CoDeepNEAT population on the MNIST handwritten digit dataset for 72 generations. Subsequently
    the best genome is trained for a final 200 epochs and its genotype and Tensorflow model are backed up.
    """
    # Set standard configuration specific to TFNE but not the neuroevolution process
    logging_level = logging.INFO
       # Parse GTFS
    #routes, stops, stop_times, trips, shapes = gtfs.import_gtfs("data/fahrplaene_gesamtdeutschland.zip")
    #routes, stops, stop_times, trips, shapes = gtfs.import_gtfs("data/fahrplaene_gesamtdeutschland.zip", busiest_date = True)
    if flags.FLAGS.logging_level is not None:
        logging_level = flags.FLAGS.logging_level
    
    # Set logging, parse config
    logging.set_verbosity(logging_level)

    if flags.FLAGS.dest_dir is not None:
        dest_dir = flags.FLAGS.dest_dir

    source_file = flags.FLAGS.source_file
    buckets = flags.FLAGS.buckets

    try:
        routes, stops, stop_times, trips, shapes = gtfs.import_gtfs(source_file)
    except:
        print("File not compatible!! .. you can only use GTFS files. Check the Doku of your set oder use Tools to transform your data!")
        quit()
    # Read in optionally supplied flags, changing the just set standard configuration
    
    cutoffs = np.arange(0, 24+1, buckets)#[range(0,24,buckets)]#[0,6,9,15,19,22,24]
    print('####### START ########')
    #print(cutoffs)
    print('####### STOP FREQUENCIES #######')
    stop_freq = gtfs.stops_freq(stop_times, stops, cutoffs = cutoffs)
    print('# calculation DONE!')
    file_name = 'stop_frequencies'
    gtfs.save_gdf(stop_freq, dest_dir + file_name, shapefile=True, geojson=True)
    print('# saving DONE as {} *.zip (shapefiles) and *.geojson'.format(file_name))

    print('\n\n')

    print('####### LINE FREQUENCIES #######')
    line_freq = gtfs.lines_freq(stop_times, trips, shapes, routes, cutoffs = cutoffs)
    print('# calculation DONE!')
    file_name = 'line_frequencies'
    gtfs.save_gdf(line_freq, dest_dir + file_name, shapefile=True, geojson=True)
    print('# saving DONE as {} *.zip (shapefiles) and *.geojson'.format(file_name))

    print('\n\n')

    print('####### SEGMENTS #######')
    segments_gdf = gtfs.cut_gtfs(stop_times, stops, shapes)
    print('# calculation DONE!')
    file_name = 'segments'
    gtfs.save_gdf(segments_gdf, dest_dir + file_name, shapefile=True, geojson=True)
    print('# saving DONE as {} *.zip (shapefiles) and *.geojson'.format(file_name))

    print('\n\n')

    print('####### SPEEDS #######')
    speeds = gtfs.speeds_from_gtfs(routes, stop_times, segments_gdf, cutoffs = cutoffs)
    print('# calculation DONE!')
    file_name = 'speeds'
    gtfs.save_gdf(speeds, dest_dir + file_name, shapefile=True, geojson=True)
    print('# saving DONE as {} *.zip (shapefiles) and *.geojson'.format(file_name))

    print('\n\n')

    print('####### SEGMENTS FREQUENCIES #######')
    seg_freq = gtfs.segments_freq(segments_gdf, stop_times, routes, cutoffs = cutoffs)
    print('# calculation DONE!')
    file_name = 'seq_freq'
    gtfs.save_gdf(seg_freq,dest_dir + file_name, shapefile=True, geojson=True)
    print('# saving DONE as {} *.zip (shapefiles) and *.geojson'.format(file_name))

    print('\n\n')
    
    print("########################### \n"
    "Thanks for using these script ... you can find more in the Project OpenPublicTransport under openpublictransport.de ... \n"
    "Support us, contact us, stay tuned!!!")
    
if __name__ == '__main__':
    app.run(calculation)