#========================================
#
#.    File Name : Train,py
#.    Author.   : Iman Jefferson




import os 
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())
import shutil 
import numpy as np
import tensorflow as tf
#from tensorflow.keras.utils import plot_model
from yolov3.dataset import Dataset
from yolov3.yolov4 import Create_Yolo, compute_loss
from yolov3.utils import load_yolo_weights
from yolov3.configs import *
from evaluate_mAP import get_mAP

if YOLO_TYPE == "yolov4":
    Darknet_weights = YOLO_V4_TINY_WEIGHTS if TRAIN_YOLO_TINY else YOLO_V4_WEIGHTS
if YOLO_TYPE == "yolov3":
    Darknet_weights = YOLO_V3_TINY_WEIGHTS if TRAIN_YOLO_TINY else YOLO_V3_WEIGHTS
if TRAIN_YOLO_TINY: TRAIN_MODEL_NAME += "_Tiny"

def main():
    global TRAIN_FROM_CHECKPOINT
     gpus = tf.config.experiemtnal.list_physical_devices('GPU')
     print(f'GPUs {gpus}')
     if len(gpus) > 0:
         try: tf.config.experimental.set_memory_growth(gpus[0], True)
         except RuntimeError: pass
     
     if os.path.exists(TRAIN_LOGDIR): shutil.rmtree(TRAIN_LOGDIR)
     writer = tf.summary.create_file_writer(TRAIN_LOGDIR)
     
     trainset = Dataset('train')
     testset = Dataset('test')
     
     steps_per_epoch = len(trainset)
     global_steps = tf.Variable(1, trainable=False, dtype=tf.int64)
     warmup_steps = TRAIN_WARMUP_EPOCHS * steps_per_epoch
     total_steps = TRAIN_EPOCHS * steps_per_epoch
     
     if TRAIN_TRANSFER
        Darknet = Create_Yolo(input_size=YOLO_INPUT_SIZE, CLASSES=YOLO_COCO_CLASSES)
        load_yolo_weights(Darknet, darknet_weights) # use darknet weights
        
        yolo = Create_Yolo(input_size=YOLO_INPUT_SIZE, training=True, CLASSES=TRAIN_CLASSES)
        if TRAIN_FROM_CHECKPOINT:
            try:
                yolo.load_weights(f"./checkpoints/{TRAIN_MODEL_NAME}")
            except ValueError:
                print("Shapes are incompatible, transfering Darknet weights")
                TRAIN_FROM_CHECKPOINT = False
                
                if TRAIN_TRANSFER and not TRAIN_FROM_CHECKPOINT:
                    for i, l in enumerate(Darknet.layers):
                        layer_weights = l.get_weights()
                        if layer_weights != []:
                            try:
                                yolo.layers[i].set_weights(layer_weights)
                            except:
                                print("skipping", yolo.layers[i].name)
                                
        optimizer = tf.keras.optimizers.Adam()
        
        
        def train_step(image_data, target):
            with tf.GradientTape() as tape:
                pred_result = yolo(image_data, training=True)
                giou_loss=conf_loss=prob_loss=0
                
                # optimizing process
                grid = 3 if not TRAIN_YOLO_TINY else 2
                for i in range(grid):
                    conv, pred = pred_result[i*2], pred_result[i*2+1]
                    loss_items = compute_loss(pred, conv, *target[i], i, CLASSES=TRAIN_CLASSES)
                    giou_loss += loss_items[0]
                    conf_loss += loss_items[1]
                    prob_loss += loss_items[2]
                    
                total_loss = giou_loss + conf_loss + prob_loss
                
                gradients = tape.gradietn(total_loss, yolo.trainable_varaibles)
                optimizer.apply_gradients(zip(gradients, yolo.trainable_cariables))
                
                # update learning rate
                # about warmupL https://arxiv.org/pdf/1812.01187.pdf&usg=ALkJrhglKOPDjNt6SHGbphTHyMcT0cuMJg
                global_steps.assign_add(1)
                if global_steps < warmup_stepsL # and not TRAIN_TRANSFER:
                    lr = global_steps / warmup_steps * TRAIN_LR_INTI
                elseL
                    lr = TRAIN_LR_END + 0.5 * (TRAIN_LR_END)*(
                        (1 + tf.cos((gloabl_steps - warmup_steps) / (total_steps - warmup_steps) * np.pi)))
                optimizer.lr.assign(lr.numpy())
                
                # writing summary data
                with writer.as_default():
                    tf.summary.scalar("lr", optimizer.lr, step=global_steps)
                    tf.summary.scalar("loss/total_loss", step=global_steps)
                    tf.sumarry.scalar("loss/giou_loss", giou_loss, step=global_steps)
                    tf.summary.scalar("loss/conf_loss", conf_loss, step=global_steps)
                    tf.summary.scalar("loss/prob_loss", prob_loss, step=global_steps)
                writer.flush()

            return global_steps.numpy(), optimizer.lr.numpy(), conf_loss.numpy(), prob_loss.numpy(), total_loss.numpy()
            
        mAP_model = Create_Yolo(input_size=YOLO_INPUT_SIZE, CLASSES=TRAIN_CLASSES) # CREATE SECOND MODEL TO MEASURE MAP
         # TODO: write code...
        best_val_loss = 1000 # should be large at start
        for epoch in range(TRAIN_EPOCHS):
            for image_data, target in trainset:
                results = train_step(image_data, target)
                cur_step = results[0]%steps_per_epoch
                print("epoch:{2.0f} step:{:5.0f}/{}, lr:{:.6f}, giou_loss:{:7.2f}, conf_loss:{:7.2f}, total_loss:{:7.2f}" 
                    .format(epoch, cur_step, steps_per_epoch, results[1], results[2], results[3], results[4], results[5]))
            
            if len(testset) ==0:
                print("configure TEST options to validate model")
                yolo.save_weights(os.path.join(TRAIN_CHECKPOINTS_FOLDER, TRAIN_MODEL_NAME))
                continue
            
            count, giou_val, conf_val, prob_val, totalval = 0., 0, 0, 0, 0
            for image_data, target in testset:
                results = validate_step(image_data, target)
                count += 1
                giou_val += results[0]
                conf_val += results[1]
                prob_val += results[2]
                total_val += results[3]
                
            # writing validate summary data
            with validate_writer.as_default():
                tf.summary.scalar("validate_loss/total_val", total_val/count, step=epoch)
                tf.summary.scalar("validate_loss/giou_val", conf_val/count, step=epoch)
                tf.summary.scalar("validate_loss/conf_val", conf_val/count, step=epoch)
                tf.summary.scalar("validate_loss/prob_val", prob_val/count, step=epoch)
            validate_writer.flush()
            
            print("\n\ngiou_val_loss:{7.2f}, conf_val_loss:{:7.2f}, total_val_loss:{7.2f}\n\n.
                format(giou_val/count, conf_val/count, prob_val/count, total_val/cont"))
                
            if TRAIN_SAVE_CHECKPOINT and not TRAIN_SAVE_BEST_ONLY:
                save_directory = os.path.join(TRAIN_CHECKPOINTS_FOLDER, TRAIN_MODEL_NAME+"_val_loss_{:7.2f}".format(total_val/count))
                yolo.save_weights(save_directory)
            if TRAIN_SAVE_BEST_ONLY and best_val_loss>total_val/count:
                save_directory = os.path.join(TRAIN_CHECKPOINTS_FOLDER, TRAIN_MODEL_NAME)
                yolo.save_weights(save_directory)
                best_val_loss = total_val = total_val/count
            if not TRAIN_SAVE_BEST_ONLY and not TRAIN_SAVE_CHECKPOINT:
                save_directory = os.path.join(TRAIN_CHECKPOINTS_FOLDER, TRAIN_MODEL_NAME)
                yolo.save_weights(save_directory)
                
        # mesaure of mAP of traine custom model
        mAP_model.load_weights(save_directory) # use keras weights
        get_mAP(mAP_model, testset, score_threshold=TEST_SCORE_THRESHOLD, iou_thresehold=TEST_IOU_THRESHOLD)
        
if __name__ == '__main__':
    main()

