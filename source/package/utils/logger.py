import logging
import functools


def log(_func=None, *, my_logger: logging.Logger = None):
    """Decorator to perform exception handling and logging

    Parameters
    ----------
    _func : object, optional
       The function wrapped by the decorator, by default None
    my_logger : logging.Logger, optional
        Logger object for logging debug and exception messages, by default None

    Raises
    ------
    Runtime error
    """
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # if no Logger passed in then create one for the function
            if my_logger is None:
                logger =logging.getLogger(func.__name__)
            else:
                logger = my_logger
            # Get the function arguments for debug messages
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            logger.debug(f"function {func.__name__} called with args {signature}")
            # Execute the function and return the result
            try:
                result = func(*args, **kwargs)
                return result
            # Catches any exception in the function
            except Exception as e:
                # Log the exception details
                logger.exception(f"Exception raised in {func.__name__}. exception: {str(e)}")
                raise RuntimeError from e
        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)

def log_class(Cls):
    """Class decortaor which will apply the log decorator to all methods in class

    Parameters
    ----------
    Cls : class
        The class being decorated

    Returns
    -------
    class
        Returns the wrapped class method
    """    
    # decoration body
    class Wrapper:
        """Modifies __init__ and __getattribute_
        for decorated classes
        """        
        def __init__(self, *args, **kwargs):
            self.decorated_obj = Cls(*args, **kwargs)
            # Get the objects logger attribrute or class variable
            # This is to pass to the log decorator
            try:
                self.logger = self.decorated_obj.logger
            except AttributeError:
                # If object has no logger then 
                # one will be created by the log decorator
                pass

        def __getattribute__(self, s):
            try:
                x = super().__getattribute__(s)
                return x
            except AttributeError:
                pass
            x = self.decorated_obj.__getattribute__(s)
            if type(x) == type(self.__init__): 
                # It is an instance method
                # So apply the log decorator to the method
                return log(x, my_logger=self.logger)
            else:
                return x

    return Wrapper  # decoration ends here