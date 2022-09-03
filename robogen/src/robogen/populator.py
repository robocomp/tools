from abc import ABC, abstractmethod

class Populator(ABC):
	def __init__(self, file, artifact):
		super().__init__()
		self.file     = file
		self.artifact = artifact

	@abstractmethod
	def populate(self):
		pass
