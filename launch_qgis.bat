@echo off
echo =================================================================
echo  Configuring Environment for FOSS4G Workshop...
echo =================================================================

rem --- Set the location of QGIS and our portable Java ---
rem --- NOTE: Path is to the root of the OSGeo4W installation ---
set QGIS_INSTALL_PATH=C:\OSGeo4W
set JAVA_HOME=%~dp0jdk\jdk-21.0.8+9


echo QGIS Path: %QGIS_INSTALL_PATH%
echo Java Path: %JAVA_HOME%

rem --- Run the standard QGIS environment setup script ---
call "%QGIS_INSTALL_PATH%\bin\o4w_env.bat"

rem --- Add our portable Java to the *front* of the path ---
set PATH=%JAVA_HOME%\bin;%PATH%

echo.
echo Environment is ready. Launching QGIS...
echo =================================================================

rem --- Launch QGIS ---
start "QGIS" /B "%QGIS_INSTALL_PATH%\bin\qgis-bin.exe"

rem --- Exit the command window ---
exit