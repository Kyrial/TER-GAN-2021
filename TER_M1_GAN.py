
from keras.datasets import mnist
from keras.layers import Input, Dense, Reshape, Flatten, Dropout
from keras.layers import BatchNormalization, Activation
from keras.layers.advanced_activations import LeakyReLU
from keras.models import Sequential, Model
from keras.optimizers import Adam

import matplotlib.pyplot as plt
import sys
import numpy as np

from keras.datasets import mnist

from keras.layers import Input, Dense, Reshape, Flatten, Dropout
from keras.layers import BatchNormalization, Activation
from keras.layers.advanced_activations import LeakyReLU
from keras.models import Sequential, Model
from keras.optimizers import Adam


verbose = False




print("miaou")

class GAN():
    def __init__(self):
        self.img_rows = 28
        self.img_cols = 28
        self.channels = 1
        self.img_shape = (self.img_rows, self.img_cols, self.channels)
        self.latent_dim = 100
        optimizer = Adam(0.0002, 0.5)        
        self.discriminator = self.build_discriminator()
        self.discriminator.compile(loss='binary_crossentropy',
            optimizer=optimizer,
            metrics=['accuracy'])       
        self.generator = self.build_generator()
        z = Input(shape=(self.latent_dim,))
        img = self.generator(z)
        self.discriminator.trainable = False
        validity = self.discriminator(img)
        self.combined = Model(z, validity)
        self.combined.compile(loss='binary_crossentropy', optimizer=optimizer)

    def build_generator(self):
        model = Sequential()
        model.add(Dense(256, input_dim=self.latent_dim))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(1024))
        model.add(LeakyReLU(alpha=0.2))
        model.add(BatchNormalization(momentum=0.8))
        model.add(Dense(np.prod(self.img_shape), activation='tanh'))
        model.add(Reshape(self.img_shape))
        model.summary()
        noise = Input(shape=(self.latent_dim,))
        img = model(noise)
        return Model(noise, img)

    def build_discriminator(self):
        model = Sequential()
        model.add(Flatten(input_shape=self.img_shape))
        model.add(Dense(512))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(256))
        model.add(LeakyReLU(alpha=0.2))
        model.add(Dense(1, activation='sigmoid'))
        model.summary()
        img = Input(shape=self.img_shape)
        validity = model(img)
        return Model(img, validity)

    def train(self, epochs, batch_size=128, sample_interval=50): 
        #(X_train, _), (_, _) = mnist.load_data()  
        #ce qu'on doit modifier !
        (X_train, Y_train), (X_test, Y_test) = mnist.load_data()  
        #print("MIAAAAAAAAOUUUUU",Y_train[1])
        #print("MIAAAAAAAAOUUUUU",X_train[1])
        #print( list( filter (lambda x: x <= 1 , Y_train)));
        print( type(X_train))
        
        filter_arr =  list(map (lambda x: True if x <= 1 else False, Y_train))

        X_train= X_train[filter_arr]
        #X_train = np.ndarray((lambda x, y: x if y <= 1 else x, X_train, Y_train))
        
        Y_train =  list(filter (lambda x: x <= 1 , Y_train))
   #    for x in range(len(X_train)):
    #       if Y_train[x] >1:
               

        
        print("0 --> ", len(list( filter (lambda x: x == 0 , Y_train))));
        print("1 --> ", len(list( filter (lambda x: x == 1 , Y_train))));

        nbr_0 =  len(list( filter (lambda x: x == 0 , Y_train)));
        nbr_1 =  len(list( filter (lambda x: x == 1 , Y_train)));

        if nbr_0 > nbr_1:
            while nbr_0 != nbr_1:
                ind = Y_train.index(0)
                Y_train.remove(0)
                np.delete(X_train, ind,0)
                nbr_0 = nbr_0 -1

        if nbr_1 > nbr_0:
            while nbr_1 != nbr_0:
                ind = Y_train.index(1)
                Y_train.remove(1)
                np.delete(X_train, ind,0)
                nbr_1 = nbr_1 -1

        print("2: 0 --> ", len(list( filter (lambda x: x == 0 , Y_train))));
        print("2: 1 --> ", len(list( filter (lambda x: x == 1 , Y_train))));
            
        
        X_train = X_train / 127.5 - 1.
       
        X_train = np.expand_dims(X_train, axis=3)
        valid = np.ones((batch_size, 1))
        fake = np.zeros((batch_size, 1))
           
        for epoch in range(epochs):
            if epoch%10==0:
                print("epoch: ",epoch)


            idx = np.random.randint(0, X_train.shape[0], batch_size)
            imgs = X_train[idx]
            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            gen_imgs = self.generator.predict(noise)
            d_loss_real = self.discriminator.train_on_batch(imgs, valid)
            d_loss_fake = self.discriminator.train_on_batch(gen_imgs, fake)
            d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)

            noise = np.random.normal(0, 1, (batch_size, self.latent_dim))
            g_loss = self.combined.train_on_batch(noise, valid)
            if verbose:
                print ("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100*d_loss[1], g_loss))
            
            if epoch % sample_interval == 0:
                self.sample_images(epoch)
    def sample_images(self, epoch):
        r, c = 5, 5
        noise = np.random.normal(0, 1, (r * c, self.latent_dim))
        gen_imgs = self.generator.predict(noise)        
        gen_imgs = 0.5 * gen_imgs + 0.5
        
        
        
        fig, axs = plt.subplots(r, c)
        cnt = 0
        for i in range(r):
            for j in range(c):
                axs[i,j].imshow(gen_imgs[cnt, :,:,0], cmap='gray')
                axs[i,j].axis('off')
                cnt += 1
        fig.savefig("images/%d.png" % epoch)
        print("image are saved !")
        plt.close()



if __name__ == '__main__':
    gan = GAN()
    gan.train(epochs=100000, batch_size=132, sample_interval=100)