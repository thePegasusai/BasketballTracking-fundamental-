# using fast.Ai library
# Import the necessary libraries 
from fastai.vision.all import * 

# Create a DataBunch object 
path = Path('data/sports_balls') 
data = ImageDataLoaders.from_folder(path, train='train', valid='valid', valid_pct=0.2, seed=42,
                                    item_tfms=Resize(224)) 

# Create and train the Learner object 
learn = cnn_learner(data, models.resnet34, metrics=error_rate) 
learn.fit_one_cycle(4) 

# Make predictions on the validation set 
interp = ClassificationInterpretation.from_learner(learn) 
interp.plot_confusion_matrix(figsize=(12,12), dpi=60) 
