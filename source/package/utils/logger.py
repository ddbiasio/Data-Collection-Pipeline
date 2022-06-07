import logging
import functools
   
def log(_func=None, *, my_logger: logging.Logger = None):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if my_logger is None:
                logger =logging.getLogger(func.__name__)
            else:
                logger = my_logger
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.debug(f"function {func.__name__} called with args {signature}")
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise RuntimeError from e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)

def log_class(Cls):
    # decoration body - doing nothing really since we need to wait until the decorated object is instantiated
    class Wrapper:
        def __init__(self, *args, **kwargs):
            self.decorated_obj = Cls(*args, **kwargs)
            try:
                self.logger = self.decorated_obj.logger
            except AttributeError:
                pass

        def __getattribute__(self, s):
            try:
                x = super().__getattribute__(s)
                return x
            except AttributeError:
                pass
            x = self.decorated_obj.__getattribute__(s)
            if type(x) == type(self.__init__):  # it is an instance method
                return log(x, my_logger=self.logger)  # this is equivalent of just decorating the method with log
            else:
                return x

    return Wrapper  # decoration ends here