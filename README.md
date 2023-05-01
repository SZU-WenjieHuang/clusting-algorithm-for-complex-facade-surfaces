### Geometric algorithm: A parameterization model and clusting algorithm for complex facade surfaces (2021.11-2022.1)
  ![image](https://user-images.githubusercontent.com/82434538/235461992-4dd8bf26-fca3-4d5a-abb8-f0145cc6336f.png)\
  ***Repository:*** [clusting algorithm for complex facade surfaces](https://github.com/SZU-WenjieHuang/clusting-algorithm-for-complex-facade-surfaces)\
  ***Data:*** The mesh information (vertex position and normal) of complex surfaces after UV mapping\
  ***Description:*** The construction of complex surface of buildings always needs to provide different molds for each panel. I hope to find the optimal pannel clusting through K-means clustering, so the same mold can correspond to different pannels, save costs in the actual construction process. Before clusting, I constructed a parameterized model for panels, using 5 parameters to difine the size and curvature of each pannel. I divied all panels into three categories: flat, single curved surface, and hyperbilic surface in first round. Then, clusting was performed within each catagory.

- #### 01 Parameterized modelg:
  Before applying clustering algorithms, it is necessary to describe the shape of the entire panel (including size and curvature) with as few parameters as possible. Therefore, I constructed two parameterized models to describe the flat panel and single curved surface.
  ![shape02](https://user-images.githubusercontent.com/82434538/235464125-380bff46-32f8-484c-9ca1-ebfd17beaf5f.jpg)
  The model for the flat panel is described using the length of the vector from the center point to the four corners, as well as the angle between them.\
  The model for a single curved surface is described using the length of the vector from the center point to the four corners, along with the radius of the corresponding cylinder formed by its curvature.\
  ![test03](https://user-images.githubusercontent.com/82434538/235464139-801141ce-70a4-4b47-9bdc-6154ff9d293d.jpg)

- #### 02 First Round Selection:
  In our first round of selection, we defined several shape error metrics to characterize the panels:\
  ***Divergence:*** quantifies the spatial gap between adjacent panels\
  ***Kink angle:*** measures the jump in normal vectors between adjacent panels\
  ***Surface fitting:*** the deviation of the curve network from surface F\
  ***Curve fairness:*** severity of tangential drift of the panels\
  ***Panel centering:*** the mold center away from the segment center
  ![image](https://user-images.githubusercontent.com/82434538/235466745-4018157d-ff03-4fe3-aa54-0f07094b5679.png)
  We first replaced all surfaces with flat panels, and if a panel did not meet the threshold, we replaced it with a single curved surface. If a single curved surface also failed to meet the threshold requirement, then we used a hyperbolic surface. Through this first round of selection, we roughly classified all panels into three categories: flat panels, single curved surfaces, and double curved surfaces.
  ![image](https://user-images.githubusercontent.com/82434538/235466915-ca19b683-7cf7-4703-bcea-105567493f6f.png)
  Blue: double curved; Yellow: single curved; Grey: flat panels


- #### 03 First Round Selection: Clusting:
  In Step 01, we obtained the parameterized data as the representation for each pannel, and then used the K-means algorithm for unsupervised learning clustering, so that pannels with similar shape coefficients could use the same template for production.\
  ![image](https://user-images.githubusercontent.com/82434538/235468032-cb8f4b7b-2488-4d7a-9bf0-bf1757cd28d9.png)\
  Based on the SSE and Silhouette data, we selected the optimal number of clusters and used it to classify all the panels.

- #### 03 Scalability:
  We can also transfer the methods applied on quadrilateral panels to triangular panels and obtain good results.
  ![image](https://user-images.githubusercontent.com/82434538/235470239-afe33a2c-a082-41e1-8dcf-cf6e5f752434.png)
  ![image](https://user-images.githubusercontent.com/82434538/235470298-579254df-d0b0-4b52-82c8-80bded8395d9.png)

  

