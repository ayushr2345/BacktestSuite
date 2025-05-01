#include <iostream>
#include <Python.h>
#include <filesystem>
#include "Backtester.h"
#include "LogMacros.h"

int main(int argc, char* argv[])
{
    if (argc < 4)
    {
        LOG_ERROR("Insufficient arguments provided. Expected 4 arguments.");
        std::cerr << "Usage: backtester <symbol> <timeframe> <start_date> <end_date>" << std::endl;
        return 1;
    }

    std::string symbol = argv[1];
    std::string timeFrame = argv[2];
    std::string startDate = argv[3];
    std::string endDate = argv[4];
    LOG_DEBUG("Symbol: {}", symbol);
    LOG_DEBUG("Time Frame: {}", timeFrame);
    LOG_DEBUG("Start Date: {}", startDate);
    LOG_DEBUG("End Date: {}", endDate);

    logger::Logger::getInstance().setLogFile("backtester.log");
    LOG_DEBUG("Backtester started");

    // Initialize the Python Interpreter
    LOG_DEBUG("Initializing Python Interpreter...");
    Py_Initialize();

    // Get current directory for debugging
    std::filesystem::path currentPath = std::filesystem::current_path();

    // Add script directory to Python path using the configured path
    PyRun_SimpleString("import sys");
    std::string dataDownloaderPath = DATA_DOWNLOADER_PATH;
    std::string pythonPath;

#ifdef _WIN32
    LOG_INFO("Windows Build System, replacing \\ with /");
    std::replace(dataDownloaderPath.begin(), dataDownloaderPath.end(), '\\', '/');
#endif // !_WIN32

    pythonPath = "sys.path.append('" + dataDownloaderPath + "')";
        
    LOG_DEBUG("Python Path: {}", pythonPath);
    PyRun_SimpleString(pythonPath.c_str());


    PyObject* pName = PyUnicode_DecodeFSDefault("DataDownloader");
    PyObject* pModule = PyImport_Import(pName);
    Py_DECREF(pName);

    if (pModule != nullptr)
    {
        PyObject* pFunc = PyObject_GetAttrString(pModule, "download_data");

        if (PyCallable_Check(pFunc))
        {
            PyObject* pArgs = PyTuple_New(4);
            PyTuple_SetItem(pArgs, 0, PyUnicode_FromString(symbol.c_str()));  // example args
            PyTuple_SetItem(pArgs, 1, PyUnicode_FromString(timeFrame.c_str()));
            PyTuple_SetItem(pArgs, 2, PyUnicode_FromString(startDate.c_str()));
            PyTuple_SetItem(pArgs, 3, PyUnicode_FromString(endDate.c_str()));

            PyObject* pValue = PyObject_CallObject(pFunc, pArgs);
            Py_DECREF(pArgs);

            if (pValue != nullptr)
            {
                LOG_DEBUG("Python function returned successfully");
                Py_DECREF(pValue);
            }
            else
            {
                PyErr_Print();
                LOG_ERROR("Python function call failed");
            }
            Py_XDECREF(pFunc);
        }
        else
        {
            PyErr_Print();
            LOG_ERROR("Python can't find function 'download_data'");
        }
        Py_DECREF(pModule);
    }
    else
    {
        PyErr_Print();
        LOG_ERROR("Python failed to load 'DataDownloader' module");
    }

    Py_Finalize();
    return 0;
}
