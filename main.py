import getopt
import os
import sys

# Make library available in path
library_paths = [
    os.path.join(os.getcwd(), "lib"),
    os.path.join(os.getcwd(), "lib", "log"),
]

for p in library_paths:
    if not (p in sys.path):
        sys.path.insert(0, p)

# Import library classes
from tracking_decorator import TrackingDecorator
from point_generator import PointGenerator
from logger_facade import LoggerFacade


#
# Main
#

@TrackingDecorator.track_time
def main(argv):
    # Set default values
    clean = False
    quiet = False
    num_sample_points = 10_000
    cities = ["berlin"]

    # Read command line arguments
    try:
        opts, args = getopt.getopt(argv, "hcqp:", ["help", "clean", "quiet", "points="])
    except getopt.GetoptError:
        print("main.py --help --clean --quiet --points <points>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("main.py")
            print("--help                           show this help")
            print("--clean                          clean intermediate results before start")
            print("--quiet                          do not log outputs")
            print("--points                         number of sample points to use")
            sys.exit()
        elif opt in ("-c", "--clean"):
            clean = True
        elif opt in ("-q", "--quiet"):
            quiet = True
        elif opt in ("-p", "--points"):
            num_sample_points = int(arg)

    # Set paths
    file_path = os.path.realpath(__file__)
    script_path = os.path.dirname(file_path)
    data_path = os.path.join(script_path, "data", "data")
    results_path = os.path.join(script_path, "results", "results")

    # Initialize logger
    logger = LoggerFacade(results_path, console=True, file=True)
    logger.log_line("Start")

    for city in cities:

        # Generate sample points
        sample_points = PointGenerator().run(
            logger=logger,
            data_path=data_path,
            results_path=os.path.join(results_path, city, "sample-points"),
            city=city,
            num_sample_points=num_sample_points,
            clean=clean,
            quiet=quiet
        )


if __name__ == "__main__":
    main(sys.argv[1:])
