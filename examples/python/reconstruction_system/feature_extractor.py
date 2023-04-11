import numpy as np
import cv2 
import argparse
import os

def feature_detector(img1,img2):
    
    orb = cv2.ORB_create(nfeatures=1000,scaleFactor=1.2,nlevels=8, edgeThreshold=31, firstLevel=0, WTA_K=2, scoreType=0, patchSize=31, fastThreshold=20)
    
    kp1, des1 = orb.detectAndCompute(img1,None)
    kp2, des2 = orb.detectAndCompute(img2,None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1,des2)
    
    matches = sorted(matches, key = lambda x:x.distance)
    
    return matches, kp1, kp2, des1, des2
    
    
def get_matched_features(matches,kp1,kp2,n_features):
    
    matched_kp1=[]
    matched_kp2=[]
    matched_kp1_pt=[]
    matched_kp2_pt=[]
    
    if n_features>len(matches):
        n_features=len(matches)
    
    for i in range(n_features):
        matched_kp1.append(kp1[matches[i].queryIdx])
        matched_kp2.append(kp2[matches[i].trainIdx])
        matched_kp1_pt.append(kp1[matches[i].queryIdx].pt)
        matched_kp2_pt.append(kp2[matches[i].trainIdx].pt)
        
    matched_kp1=np.asarray(matched_kp1)
    matched_kp2=np.asarray(matched_kp2)
    matched_kp1_pt = np.asarray(matched_kp1_pt)
    matched_kp2_pt = np.asarray(matched_kp2_pt)
    return matched_kp1,matched_kp2, matched_kp1_pt, matched_kp2_pt



def visualize_correspondences(path, indices):
        
    for i in range(len(indices) - 1):
        
        img1 = cv2.imread(os.path.join(path, '{}.png'.format(indices[i])))
        img2 = cv2.imread(os.path.join(path, '{}.png'.format(indices[i])))
        
        matches, kp1, kp2, des1, des2 =feature_detector(img1,img2)
        img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches,None)
        cv2.imshow("Correspondences",img3)
        
        k=cv2.waitKey(200)
        if (k==ord('q')): break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Feature Matching")
    parser.add_argument("--path",
                        help="path to the datset folder containing color and depth image folders",
                        default = "dataset/"
                        )
    parser.add_argument("--level",
                        help="Number of splits we want in the image",
                        default = 1
                        )
    parser.add_argument("--threshold",
                        help="Number of splits we want in the image",
                        default = 0.75
                        )
    parser.add_argument("--correspondences",
                        help="Whether to visualize correspondences",
                        action="store_true"
                        )
    
    

    args = parser.parse_args()
    
    level = int (args.level)
    threshold = float(args.threshold)
    path = args.path
    color_path = os.path.join(path, "color")
    depth_path = os.path.join(path, "depth")
    
    
    length = len(os.listdir(color_path))
    i = 0
    images = []
    images.append(i)
    img_temp=cv2.imread(os.path.join(color_path, '{}.png'.format(0)),cv2.IMREAD_GRAYSCALE)
    w, h = img_temp.shape
    w2 = int (w/2)
    h2 = int(h/2)
    
    print("EXTRACTING USEFUL FRAMES")
    while (i < length - 1):
        img1=cv2.imread(os.path.join(color_path, '{}.png'.format(i)),cv2.IMREAD_GRAYSCALE)
        img1_coloured=cv2.imread(os.path.join(color_path, '{}.png'.format(i)))
        
        common_features = 1000
        common_features_percent = 1
        
        # while(common_features > 600 and i < length - 1):
        while(common_features_percent > threshold  and i < length - 1):
            i += 1
            img2=cv2.imread(os.path.join(color_path, '{}.png'.format(i)),cv2.IMREAD_GRAYSCALE)
            img2_coloured=cv2.imread(os.path.join(color_path, '{}.png'.format(i)).format(i))
            
            if level == 2:
                matches1, kp11, kp21, des11, des21 =feature_detector(img1[0:w2,0:h2],img2[0:w2,0:h2])
                # cfp1 = len(matches1)/len(kp11)
                cfp1 = len(matches1)
                
                matches2, kp12, kp22, des12, des22 =feature_detector(img1[w2:,h2:],img2[w2:,h2:])
                # cfp2 = len(matches2)/len(kp12)
                cfp2 = len(matches2)
                
                matches3, kp13, kp23, des13, des23 =feature_detector(img1[w2:,0:h2],img2[w2:,0:h2])
                # cfp3 = len(matches3)/len(kp13)
                cfp3 = len(matches3)
                
                
                matches4, kp14, kp24, des14, des24 =feature_detector(img1[0:w2,h2:],img2[0:w2,h2:])
                # cfp4 = len(matches4)/len(kp14)
                cfp4 = len(matches4)
                
                common_features_percent = 4*(cfp1*len(kp11) + cfp2*len(kp12) + cfp3*len(kp13) + cfp4*len(kp14))/(len(kp11) + len(kp12) + len(kp13) + len(kp14))**2
               
                
            else:
                matches, kp1, kp2, des1, des2 =feature_detector(img1,img2)
                common_features_percent = len(matches)/len(kp1)
            
        images.append(i)
    print("Image Indices: ",images)
    print("Num of images: ",len(images))
    
    for i in range(length):
        if (i not in images):
            os.remove(os.path.join(color_path, '{}.png'.format(i)))
            os.remove(os.path.join(depth_path, '{}.png'.format(i)))
    
    
    if args.correspondences:
        visualize_correspondences(color_path, images)
    
    else:
        for i in range(len(images)):
            img = cv2.imread(os.path.join(color_path, '{}.png'.format(images[i])))
            
            cv2.imshow('Images for reconstruction',img)
            k=cv2.waitKey(50)
            if (k==ord('q')): break
            cv2.destroyAllWindows()
        