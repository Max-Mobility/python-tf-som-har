from matplotlib import pyplot as plt
import numpy as np
import csv
from som import SOM
 
SOM_X = 2
SOM_Y = 3
MYO_DATA_DIM = 10
SOM_ITER = 100

myo_data = [];

if __name__ == '__main__':

    inputFilename = 'myo_raw_data.csv'
    header = '% qx, qy, qz, qw, ax, ay, az, gx, gy, gz\n'

    try:
        f = open(inputFilename, 'r')
    except Exception as error:
        print("ERROR: Couldn't read from {}".format(inputFilename))
    else:
        with f:
            reader = csv.reader(f)
            for row in reader:
                if row[0][0] is not '%':
                    myo_data.append(row)
            print myo_data[0]

    #Training inputs for Myo data (quat, accel, gyro)
    som_data = np.array(myo_data)

    #Train a 20x30 SOM with 400 iterations
    som = SOM(SOM_X, SOM_Y, MYO_DATA_DIM, SOM_ITER)
    som.train(som_data)
    
    #Get output grid
    image_grid = som.get_centroids()
    
    #Plot
    plt.imshow(image_grid)
    plt.title('Myo SOM')
    plt.show()
