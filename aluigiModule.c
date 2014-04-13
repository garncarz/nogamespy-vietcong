// Copyright (C) 2014 Ondřej Garncarz
// License: AGPLv3+

#include <Python.h>

int enctype2_encoder(unsigned char *key, unsigned char *data, int size);

static PyObject* encodeList(PyObject* self, PyObject* args) {
	unsigned char *key, *data_arg, *data;
	int size, ret_size;
	PyObject *ret;
	
	if (!PyArg_ParseTuple(args, "sy#", &key, &data_arg, &size)) {
		return NULL;
	}

	data = (unsigned char*)malloc(2 * size * sizeof(unsigned char));
	memcpy(data, data_arg, size * sizeof(unsigned char));

	ret_size = enctype2_encoder(key, data, size);

	ret = Py_BuildValue("y#", data, ret_size - 1);
	free(data);
	
	return ret;
}

static PyMethodDef aluigiMethods[] = {
	{"encodeList", encodeList, METH_VARARGS},
	{NULL, NULL}
};

static struct PyModuleDef aluigiModule = {
	PyModuleDef_HEAD_INIT,
	"aluigi",
	NULL,
	0,
	aluigiMethods
};

PyMODINIT_FUNC PyInit_aluigi(void) {
	return PyModule_Create(&aluigiModule);
}

