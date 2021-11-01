from datetime import datetime

class TrackingDecorator(object):

    def track_time(func):

        def wrap(self, *args, **kwargs):
            if "logger" in kwargs:
                logger = kwargs["logger"]
            else:
                logger = None

            start_time = datetime.now()

            if logger is not None:
                logger.log_line("\n" + func.__qualname__ + " started")
            else:
                print("\n" + func.__qualname__ + " started")

            result = func(self, *args, **kwargs)

            time_elapsed = datetime.now() - start_time

            if logger is not None:
                logger.log_line(func.__qualname__ + " finished in {}".format(time_elapsed))
            else:
                print(func.__qualname__ + " finished in {}".format(time_elapsed))

            return result

        return wrap
