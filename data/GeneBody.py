
class GenePicBody():
    def __init__(self) -> None:
        self.__prompt: str = ""
        self.__size: str = ""
        
    def get_prompt(self):
        return self.__prompt
         
    def set_prompt(self, prompt: str):
        self.__prompt = prompt

    def get_size(self):
        return self.__size
    
    def set_size(self, size: str):
        self.__size = size
        
class GeneScriptBody():
    def __init__(self) -> None:
        self.__time: int = 0
        self.__title: str = ""
        self.__story: str = ""
        self.__error: bool = False
    
    def get_time(self):
        return self.__time
    
    def set_time(self, time: int):
        self.__time = time
        
    def get_title(self):
        return self.__title
    
    def set_title(self, title: str):
        self.__title = title
        
    def get_story(self):
        return self.__story
    
    def set_story(self, story: str):
        self.__story = story
        
    def get_error(self):
        return self.__error
    
    def set_error(self, error: bool):
        self.__error = error