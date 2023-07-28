#include <iostream>
#include <vector>
#include <cmath>
#include <thread>

int *getDim(float x, float y, float width, float length, float resolution)
{
  // compute how big one pixel is
  float pixSize = 1.0 / resolution;

  // round up the width and length to the nearest pixel
  float newWidth = ceil(width / pixSize) * pixSize;
  float newLength = ceil(length / pixSize) * pixSize;

  // set limits
  float xMin = x;
  float xMax = x + newWidth;

  float yMin = y;
  float yMax = y + newLength;

  // how many pixes wide and long is the region?
  int widthPix = ceil(width / pixSize);
  int lengthPix = ceil(length / pixSize);

  // make an int tuple
  int *pixCount = new int[2];
  pixCount[0] = widthPix;
  pixCount[1] = lengthPix;

  return pixCount;
}

void getRegionWorker(int *scans, float *positions, int scanCount, int scanLength, float binStart, float binEnd, float binSize, float x, float y, float z, float width, float length, float resolution, int scanStart, int scanEnd, int64_t *region)
{

  // compute how big one pixel is
  float pixSize = 1.0 / resolution;
  float pixSizeRecip = resolution;

  // round up the width and length to the nearest pixel
  float newWidth = ceil(width / pixSize) * pixSize;
  float newLength = ceil(length / pixSize) * pixSize;

  // set limits
  float xMin = x;
  float xMax = x + newWidth;

  float yMin = y;
  float yMax = y + newLength;

  // how many pixes wide and long is the region?
  int widthPix = ceil(width / pixSize);
  int lengthPix = ceil(length / pixSize);

  // 0 the allocated region
  for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
  {
    region[ptr] = 0;
  }

  // for each scan
  for (int scan = scanStart; scan < scanEnd; scan++)
  {
    // get the start position of the scan
    int scanBeginIndex = scan * scanLength;

    // get the start position of the position data
    int posBeginIndex = scan * 4;

    // get x, y, z, angle of the scan
    float scanX = positions[posBeginIndex];
    float scanY = positions[posBeginIndex + 1];
    float scanZ = positions[posBeginIndex + 2];
    float angle = positions[posBeginIndex + 3];

    float zDiff = scanZ - z;
    float zDist = zDiff * zDiff;

    // compute the angle regions
    float delta = 0.785398; // 45 degrees in radians
    float leftSlope = tan(angle + delta);
    float rightSlope = tan(angle - delta);

    // figure out what reduction mode we are in
    // and also set bounds
    bool xMode = true;

    int yMinPix = 0;
    int yMaxPix = lengthPix;
    int xMinPix = 0;
    int xMaxPix = widthPix;

    // used to compute bounds later
    // y = mx + b format
    // these are also in *real* coordinates, not pix
    float topM = 0;
    float topB = 0;
    float bottomM = 0;
    float bottomB = 0;

    // it pretty much depends on the quadrant
    if (angle >= 0.785398 && angle <= 2.35619)
    {
      // Case 1: x mode y>=0
      xMode = false;

      // computes the pixel of y=0, and sets the bounds
      // this may miss a few pixels, but its ok
      xMinPix = std::fmax(-xMin * pixSizeRecip, 0.0);

      // set top & bottom bounds
      topM = 1 / rightSlope;
      topB = scanX;
      bottomM = 1 / leftSlope;
      bottomB = scanX;
    }
    else if (angle > 2.35619 && angle < 3.92699)
    {
      // Case 2: y mode x<= 0
      xMode = true;

      // computes the pixel of x=0, and sets the bounds
      yMaxPix = std::fmin(-yMin * pixSizeRecip, lengthPix);

      // set top & bottom bounds
      topM = rightSlope;
      topB = scanY;
      bottomM = leftSlope;
      bottomB = scanY;
    }
    else if (angle >= 3.92699 && angle <= 5.49779)
    {
      // Case 3: x mode y<=0
      xMode = false;

      // computes the pixel of y=0, and sets the bounds
      xMaxPix = std::fmin(-xMin * pixSizeRecip, widthPix);

      // set top & bottom bounds
      topM = 1 / leftSlope;
      topB = scanX;
      bottomM = 1 / rightSlope;
      bottomB = scanX;
    }
    else
    {
      // Case 4: y mode x>=0
      xMode = true;

      // computes the pixel of x=0, and sets the bounds
      yMinPix = std::fmax(-yMin * pixSizeRecip, 0.0);

      // set top & bottom bounds
      topM = leftSlope;
      topB = scanY;
      bottomM = rightSlope;
      bottomB = scanY;
    }

    // iterate over the region
    // Note: This is ugly, but its fast

    if (!xMode)
    {
      // y-mode (change x ranges based on top and bottom)
      for (int pixY = yMinPix; pixY < yMaxPix; pixY++)
      {

        // compute the x and z components of the distance between the scan and the pixel

        float pixPosY = yMin + pixSize * pixY;
        float pixPosYdiff = scanY - pixPosY;
        float yDist = pixPosYdiff * pixPosYdiff;
        int yOffset = pixY * lengthPix;

        // recalculate x bounds based on top and bottom
        int xAngMax = ((topM * pixPosY + topB) - xMin) * pixSizeRecip;
        int xAngMin = ((bottomM * pixPosY + bottomB) - xMin) * pixSizeRecip;

        int xAngMaxPix = std::min(xAngMax, widthPix);
        int xAngMinPix = std::max(xAngMin, 0);

        for (int pixX = xAngMinPix; pixX < xAngMaxPix; pixX++)
        {
          // compute the distance
          float pixPosXdiff = scanX - (xMin + pixSize * pixX);
          float dist = sqrt(yDist + zDist + pixPosXdiff * pixPosXdiff);

          // are we within range of the radar?
          if (dist > binEnd || dist < binStart)
          {
            continue;
          }

          // get the bin number
          int bin = (dist - binStart) / binSize;

          // get the value of the bin
          int binValue = scans[scanBeginIndex + bin];

          // update the pixel value
          region[yOffset + pixX] += binValue;
        }
      }
    }
    else
    {
      // x-mode (change y ranges based on top and bottom)
      for (int pixX = xMinPix; pixX < xMaxPix; pixX++)
      {

        // compute the x and z components of the distance between the scan and the pixel
        float pixPosX = xMin + pixSize * pixX;
        float pixPosXdiff = scanX - pixPosX;
        float xDist = pixPosXdiff * pixPosXdiff;

        // recalculate y bounds based on top and bottom
        int yAngMax = ((topM * pixPosX + topB) - yMin) * pixSizeRecip;
        int yAngMin = ((bottomM * pixPosX + bottomB) - yMin) * pixSizeRecip;

        int yAngMaxPix = std::min(yAngMax, lengthPix);
        int yAngMinPix = std::max(yAngMin, 0);

        int pixPos = (yAngMinPix - 1) * lengthPix + pixX;

        for (int pixY = yAngMinPix; pixY < yAngMaxPix; pixY++)
        {

          // compute the distance
          float pixPosYdiff = scanY - (yMin + pixSize * pixY);
          float dist = sqrt(xDist + zDist + pixPosYdiff * pixPosYdiff);

          pixPos += lengthPix;

          // are we within range of the radar?
          if (dist > binEnd || dist < binStart)
          {
            continue;
          }

          // get the bin number
          int bin = (dist - binStart) / binSize;

          // get the value of the bin
          int binValue = scans[scanBeginIndex + bin];

          // update the pixel value
          region[pixPos] += binValue;
        }
      }
    }
  }
}

int64_t *getRegion(int *scans, float *positions, int scanCount, int scanLength, float binStart, float binEnd, float binSize, float x, float y, float z, float width, float length, float resolution)
{
  // split the work into max-2 threads
  int nthreads = std::thread::hardware_concurrency();
  std::cout << "Detected " << nthreads << " threads.\nUsing " << nthreads - 2 << " threads for computation.\n";

  int threadCount = nthreads - 2;

  // get the dimension of the region
  int *dim = getDim(x, y, width, length, resolution);
  int widthPix = dim[0];
  int lengthPix = dim[1];

  // allocate blocks of memory for the region
  std::vector<int64_t *> regions;

  for (int i = 0; i < threadCount; i++)
  {
    int64_t *region = new int64_t[widthPix * lengthPix];
    regions.push_back(region);
  }

  // split the work into threads
  int scanPerThread = scanCount / threadCount;
  std::vector<std::thread> threads;

  for (int i = 0; i < threadCount; i++)
  {
    int scanStart = i * scanPerThread;
    int scanEnd = (i + 1) * scanPerThread;

    if (i == threadCount - 1)
    {
      scanEnd = scanCount;
    }

    std::thread t(getRegionWorker, scans, positions, scanCount, scanLength, binStart, binEnd, binSize, x, y, z, width, length, resolution, scanStart, scanEnd, regions[i]);

    threads.push_back(std::move(t));
  }

  // sum the regions
  int64_t *region = new int64_t[widthPix * lengthPix];
  for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
  {
    region[ptr] = 0;
  }

  // wait for the threads to finish
  for (int i = 0; i < threadCount; i++)
  {
    threads[i].join();
  }

  for (int i = 0; i < threadCount; i++)
  {
    for (int ptr = 0; ptr < widthPix * lengthPix; ptr++)
    {
      region[ptr] += regions[i][ptr];
    }
  }

  return region;
}

extern "C"
{
  int64_t *bp_getRegion(int *scans, float *positions, int scanCount, int scanLength, float binStart, float binEnd, float binSize, float x, float y, float z, float width, float length, float resolution)
  {
    // allocate memory for scans
    int *scansPtr = new int32_t[scanCount * scanLength];
    std::copy(scans, scans + scanCount * scanLength, scansPtr);

    // allocate memory for positions
    float *positionsPtr = new float[scanCount * 4];
    std::copy(positions, positions + scanCount * 4, positionsPtr);

    return getRegion(scansPtr, positionsPtr, scanCount, scanLength, binStart, binEnd, binSize, x, y, z, width, length, resolution);
  }

  int *bp_getDim(float x, float y, float width, float length, float resolution)
  {
    return getDim(x, y, width, length, resolution);
  }
}