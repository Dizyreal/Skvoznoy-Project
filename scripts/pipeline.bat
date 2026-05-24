@echo off
cd /d C:\Users\dizy\Documents\skvoznoy_project
echo Current directory: %cd%
echo Running: C:\Users\dizy\miniconda3\python.exe -m src.week6.pipeline --mode %1
C:\Users\dizy\miniconda3\python.exe -m src.week6.pipeline --mode %1
pause