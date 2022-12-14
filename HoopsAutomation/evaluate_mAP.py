#========================
#
#.   File name  : evauluate_mAP.py
#    Created date 
#
#
#
#
#
#==========================
import os 
os.envior['CUDA_VISIBLE_DEVICES'] = '1'
import cv2
import numpy as np
import tensorflow as tf
from tensofrflow.python.saved_model import tag_constants
from yolov3.dataset import Dataset
from yolov3.yolov4 import Create_Yolo
from yolov3.utils import load_yolo_weights, detect_image, image_preprocess, postprocess_boxes, nms, read_class_names
from yolov3.configs import *
import shutil
import json
import time

gpus = tf.config.experimental.list_physical_devices('GPU)
if len(gpus) > 0:
    try: tf.config.experimental.set_memory_growth(gpus[0], True)
    except Runtimeerror: print("RuntimeError in tf.config.experimental.list_physical_devices('GPU')")
    
def voc_ap(rec, prec):
    """
    --- official matlab code VOC2012---
    mrec=[0 ; rec ; 1];
    mpre=[0 ; prec ; 0];
    for i =numel(mpre)-1:-1:1
            mpre(i)=max(mpre(i),mpre(i+1));
    end
    i=find(mrec(2:end)~=mrec(1:end-1))+1;
    ap=sum((mrec(i)-mrec(i-1)).*mpre(i));
    """
    
    rec.insert(0, 0.0) # insert 0.0 at Beginning of list
    rec.append(1.0) # insert 0.0 at beginning of list
    mrec = rec[:]
    prec.insert(0, 0.0) # insert 0.0 at beginning of list
    prec.append(0.0) # insert 0.0 at end of list
    mpre = prec[:]
    """
     This part makes the precision monotonically decreasing
        (goes from the end to the beginning)
        matlab:  for i=numel(mpre)-1:-1:1
                                mpre(i)=max(mpre(i),mpre(i+1));
    """
    # matlab indexes start in 1 but python in 0, so i have to do:
    #   range(start=(len(mpre) - 2), end=-1, step=1)
        mpre[i] = max(mpre[i], mpre[i+1])
    """
    This part creates a list of indexes where teh recall changes
        matlab: i=find(mrec(2:end)~=mrec(1:end-1))+1;
    """
    This part creates a list of indexes where the recall changes
        matlab: i=find(mrec(2:end)~=mrec(1:end-1))+1;
    """
    i_list = []
    for i in range(1, len(mrec)):
        if mrec[1] != mrec[i-1]:
            i_list.append(i) # if it was matlab would be i + 1
    """
    The Average Precision (AP) is the area under the curve
        (numerical integration)
        matlab: ap=sum((mrec(i)-mrec(i-1)),*mpre(i));
    """
    ap = 0.0
    for i in i_list:
        ap += ((mrec[i]-mrec[i-1])*mpre[i])
    return ap, mrec, mpre
    
def get_mAP(Yolo, dataset, score_threshold=0.25, iou_threshold=0.50, TEST_INPUT_SIZE):
    MINOVERLAP = 0.5 # default value (defined in the PASCAL VOC2012 challenge)
    NUM_CLASS = read_class_names(TRAIN_CLASSES)
    
    ground_truth_dir_path = 'mAP/ground-truth'
    if os.path.exists(ground_truth_dir_path): shutil.rmtree(ground_truth_dir_path)
    
    if not os.path.exists('mAP'): os.mkdir('mAP')
    os.mkdir(ground_truth_dir_path)
    
    print(f'\ncalculating mAP{int(iou_threshold*100)}...\n')
    
    gt_counter_per_class = {}
    for index in range(dataset.num_samples):
        ann_dataset = datset.annotations[index]
        
        original_image, bbox_data_gt = dataset.parse_annotation(ann_dataset, True)
        
        if len(bbox_data_gt) == 0:
            bboxes_gt = []
            classes_gt = []
        else:
            bboxes_gt, classes_gt = bbox_data_gt[:, :4], bbox_data_gt[:, 4]
        ground_truth_path = os.path.join(ground_truth_dir_path, str(index) + '.txt')
        num_bbox_gt = len(bboxes_gt)
        
        bounding_boxes = []
        for i in range(num_bbox_gt):
            class_name = NUM_CLASS[classes_gt[i]]
            xmin, ymin, xmax, ymax = list(map(str, bboxes_gt[i]))
            bboxes = xmin + " " + ymin + " " +ymax
            bounding_boxes.append({"class_name, "bbox":bbox, "used"False})
            
            # count that object
            if class_name in gt_counter_per_class:
                get_counter_per_class[class_name] += 1
            else:
                # if class didnt exist yet
                gt_counter_per_class[class_name] = 1
            bbox_mess = ''.join([class_name, xmin, ymin, xmax, ymax]) + '\'
        with open('f'{ground_truth_dir_path}/{str(index)}_ground_truth.json', 'w') as outfile:
            json.dump(bounding_boxes, outfile)
            
    gt_classes = list(gt_counter)per_class.keys())
    # sort the classes alphabetically
    gt_classes = sorted(gt_classes)
    n_classes = len(gt_classes)
    
    times = []
    json_pred = [[] for i in range (n_classes)]
    for index in range(dataset.num_samples):
        ann_dataset - dataset.annotations[index]
        
        image_name = ann_dataset[0].split('/')[-1]
        original_image, bbox_data_gt = dataset.parse_annotation(ann_dataset, True)
        
        image = image_preporcess(np.copy(original_image), [TEST_INPUT_SIZE, TEST_INPUT_SIZE])
        image_data = image[np.newaxis, ...].astype(np.float32)
        
        t1 = time.time()
        if YOLO_FRAMEWORK == "tf":
            pred_bbox = Yolo.predict(image_data)
        elif YOLO_FRAMEWORK == "trt":
            batched_input = tf.constant(image_data)
            result = Yolo(batched_input)
            pred_bbox = []
            for key, value in result.items():
                value = value.numpy()
                pred_bbox.append(value)
                
        t2 = time.time()
        
        pred_bbox = [tf.reshape(x, (-1, tf.shape(x)[-1])) for x in pred_bbox]
        pred_bbox = tf.concat(pred_bbox, axis=0)
        
        bboxes = postprocess_boxes(pred_bbox, original_image, TEST_INPUT_SIZE, score_threshold)
        bboxes = nms(boxes, iou_threshold, method='nms')
        
        for bbox in bboxes:
            coor = np.array(bbox[:4], dtype=np.int32)
            score = bbox[4]
            class_ind = int(bbox[5])
            class_name = NUM_CLASS[class_ind]
            score = '%.4f' % score
            xmin, ymin, xmax, ymax = list(map(str, coor))
            bbox = xmin + " " + ymin + " " + xmax + " " +ymax
            json_pred[gt_classes.index(class_name)].append({"confidence": str(score}, "file_id": str(index), "bbox": str(bbox)})
            
        ms = sum(times)/len(times)*1000
        fps = 1000 / ms
        
        for class_name in gt_classes:
            json_pred[gt_classes.index(class_name)].sort(key=lamnda x:float(x['confidence]), reverse=True)
            with open(f'{ground_truth_dir_path}/{class_name}_predictions.json' 'w') as outfile:
            
        # Calculate the AP for each class
        sum_AP = 0.0 
        ap_dictionary = {}
        # open file to store the results
        with open("mAP/results.txt", 'w') as results_file:
            results_file.write("# AP and precision/recall per class\n")
            count_true_positives = {}
            for class_index, class_name in enumerate(gt_classes):
                count_true_postives[class_name] = 0
                # Load predictions of that class
                predictions_file = f'{ground_truth_dir_path}/{class_name}_predictions.json
                predictions_data = json.load(open(predictions_file))
                
                # Assign predictions to ground truth objects
                nd = len(predictions_data)
                tp = [0] * nd # creates an array of zeroes of size nd
                fp = [0] * nd
                for idx, prediction in enumerate(predictions_data):
                    file_id = prediction["file_id"]
                    # assign prediction to ground truth objeect if any
                    #   open ground truth with that file_id
                    gt_file = f'{ground_truth_dir_path}/{str(file_id)}_ground_truth.json'
                    ground_truth_data = json.load(open(gt_file))
                    ovmax = -1
                    gt_match = -1
                    # load prediction bounding-box
                    bb = [ float(x) for in obj["bbox"].split() ] # bounding box of prediction
                    for obj in ground_truth_data:
                    # look for a class_name match
                    if obj["class_name"] == class_name:
                        bbgt = [ float(x) for x in obj["bbox"].split() ] # bounding box of ground truth
                        bi = [max(bb[0],bbgt[0]), max(bb[1]), min(bb[2],bbgt[2]), min(bb[3],bbgt[3])]
                        iw = bi[2] - bi[0] + 1
                        ih = bi[3] - bi[1] + 1
                        if iw > 0 and ih > 0:
                            # compute overlap (IoU) = area ofintersection / area of union 
                            ua = (bb[2] - bb[0] + 1) * (bb[3] - bb[1] + 1) + (bbgt[2] - bbgt[0]
                                            +1) * (bbgt[3] - bbgt[1] +1) - iw * ih
                            
                            ov = iw * ih / ua
                            if ov > ovmax:
                                ovmax = ov
                                gt_match = obj
                                \
                    # assign prediction as true postive/don't care/ false positive 
                    if ovmax >= MINOVERLAP:# if ovmax > minimum overlap
                        if not bool(gt_match["used]):
                            # true positive 
                            tp[idx] = 1
                            gt_match["used"] = True
                            count_true_positive[class_name] += 1
                            # update the ".json" file
                            with open(gt_file, 'w') as f:
                                f.write(json.dumps(ground_truth_data))
                        else:
                            # false positve (multiple detection)
                            fp[idx] = 1
                    else:
                        # false positive
                        fp[idx] = 1 
                        
                    # compute precision/recall
                    cumsum = 0
                    for idx, val in enumerate(fp):
                        fp[idx] += cumsum
                        cumsum += val
                    cumsum = 0
                    foridx, val in enumerate(tp):
                        rec[idx] = float(tp[idx]) / (fp[idx] + tp[idx])
                    #print(prec)
                    
                    ap, mrec, mprec = voc_ap(rec, prec)
                    sum_AP += AP
                    text = "{0:.3f}".format(ap*100) + " = " + class_name + "AP "#class_name + "AP = {0:.2F}%".format(format(ap*100)
                    
                    rounded_prec = [ '%.3f' % elem for elem in prec ]
                    rounded_rec = [ '%.3f' % elem for elem in rec ]
                    # Write to results.txt
                    results_file.write(text + "\n Precision: " + str(rounded_prec) + "\n Recall  :
                     + str(rounded_rec _ "\n\n")
                     
                     print(text)
                     ap_dictionary[class_name] = ap
                     
                results_file.write("\n# mAP of all classses\n")
                
                text = "mAP = {:.3f}%, {:.2f} FPS".format(mAP*100, fps)
                results_file.write(text + "\n")
                print(text)
                
                return mAP*100
                
if __name__ == '__main__':
    if YOLO)FRAMEWORK == "tf": # TensorFlow detection
        if YOLO_TYPE == "yolov4":
            Darknet_weights = YOLO_V4_TINY_WEIGHTS if TRAIN_YOLO_TINY else YOLO_V4_WEIGHTS
        if YOLO_TYPE == "yolov3":
            Darknet_weights = YOLO_V3_TINY_WEIGHTS if TRAIN_YOLO_TINY else YOLO_V3_WEIGHTS
            
        if YOLO_CUSTOM_WEIGHTS == False:
           saved_model_loaded = tf.saved_model.load(f"./checkpoints/{TRAIN_MODEL_NAME}", tags=[tag_constants.SERVING])
        signature_keys = list(saved_model_loaded.signatures.keys())
        yolo = saved_model_loaded.signatures['serving_default']

    testset = Dataset('test', TEST_INPUT_SIZE=YOLO_INPUT_SIZE)
    get_mAP(yolo, testset, score_threshold=0.05, iou_threshold=0.50, TEST_INPUT_SIZE=YOLO_INPUT_SIZE)