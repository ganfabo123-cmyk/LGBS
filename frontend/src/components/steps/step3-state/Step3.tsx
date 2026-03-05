import React, { useState } from 'react';
import { useProjectStore } from '../../../store/useProjectStore';
import { generateId } from '../../../lib/utils';
import type { StateVariable, DataType, UpdateMechanism } from '../../../types/project';

const Step3: React.FC = () => {
  const globalState = useProjectStore((state) => state.project.globalState);
  const addStateVariable = useProjectStore((state) => state.addStateVariable);
  const setCurrentStep = useProjectStore((state) => state.setCurrentStep);
  
  const [newVariableName, setNewVariableName] = useState('');
  const [newVariableType, setNewVariableType] = useState<DataType>('str');
  const [newVariableUpdateMechanism, setNewVariableUpdateMechanism] = useState<UpdateMechanism>('overwrite');
  const [newVariableDescription, setNewVariableDescription] = useState('');

  const handleAddStateVariable = () => {
    if (newVariableName) {
      addStateVariable({
        id: generateId(),
        name: newVariableName,
        type: newVariableType,
        updateMechanism: newVariableUpdateMechanism,
        description: newVariableDescription,
      });
      setNewVariableName('');
      setNewVariableType('str');
      setNewVariableUpdateMechanism('overwrite');
      setNewVariableDescription('');
    }
  };

  return (
    <div className="max-w-5xl">
      <h2 className="text-2xl font-bold mb-6 text-indigo-400">Step 3: Global State</h2>
      
      <div className="mb-8">
        <h3 className="text-lg font-medium mb-4 text-zinc-300">Add New State Variable</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-1">Name</label>
            <input
              type="text"
              value={newVariableName}
              onChange={(e) => setNewVariableName(e.target.value)}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
              placeholder="Variable name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-1">Type</label>
            <select
              value={newVariableType}
              onChange={(e) => setNewVariableType(e.target.value as DataType)}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
            >
              <option value="str">String</option>
              <option value="list">List</option>
              <option value="dict">Dict</option>
              <option value="int">Integer</option>
              <option value="bool">Boolean</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-1">Update Mechanism</label>
            <select
              value={newVariableUpdateMechanism}
              onChange={(e) => setNewVariableUpdateMechanism(e.target.value as UpdateMechanism)}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
            >
              <option value="overwrite">Overwrite</option>
              <option value="append">Append</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-1">Description</label>
            <input
              type="text"
              value={newVariableDescription}
              onChange={(e) => setNewVariableDescription(e.target.value)}
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100"
              placeholder="Description"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={handleAddStateVariable}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white font-medium"
          >
            Add Variable
          </button>
        </div>
      </div>
      
      <div className="space-y-4">
        {globalState.length === 0 ? (
          <div className="text-center py-12 bg-zinc-800 border border-zinc-700 rounded-md">
            <p className="text-zinc-400">No state variables added yet</p>
            <p className="text-zinc-500 text-sm mt-2">Click "Add Variable" to create your first state variable</p>
          </div>
        ) : (
          <div className="bg-zinc-800 border border-zinc-700 rounded-md overflow-hidden">
            <div className="grid grid-cols-4 gap-4 px-4 py-3 bg-zinc-700">
              <div className="font-medium text-zinc-300">Name</div>
              <div className="font-medium text-zinc-300">Type</div>
              <div className="font-medium text-zinc-300">Update Mechanism</div>
              <div className="font-medium text-zinc-300">Description</div>
            </div>
            {globalState.map((variable) => (
              <StateVariableCard key={variable.id} variable={variable} />
            ))}
          </div>
        )}
      </div>
      
      <div className="mt-8 flex justify-end space-x-4">
        <button
          onClick={() => setCurrentStep(2)}
          className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100"
        >
          Back
        </button>
        <button
          onClick={() => setCurrentStep(4)}
          disabled={globalState.length === 0}
          className={`px-4 py-2 rounded-md font-medium ${globalState.length === 0 ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}
        >
          Next
        </button>
      </div>
    </div>
  );
};

interface StateVariableCardProps {
  variable: StateVariable;
}

const StateVariableCard: React.FC<StateVariableCardProps> = ({ variable }) => {
  const updateStateVariable = useProjectStore((state) => state.updateStateVariable);
  const deleteStateVariable = useProjectStore((state) => state.deleteStateVariable);
  
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(variable.name);
  const [type, setType] = useState<DataType>(variable.type);
  const [updateMechanism, setUpdateMechanism] = useState<UpdateMechanism>(variable.updateMechanism);
  const [description, setDescription] = useState(variable.description || '');

  const handleSave = () => {
    updateStateVariable(variable.id, {
      name,
      type,
      updateMechanism,
      description,
    });
    setEditing(false);
  };

  return (
    <div className="grid grid-cols-4 gap-4 px-4 py-3 border-t border-zinc-700">
      {editing ? (
        <>
          <div>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
            />
          </div>
          <div>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as DataType)}
              className="w-full px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
            >
              <option value="str">String</option>
              <option value="list">List</option>
              <option value="dict">Dict</option>
              <option value="int">Integer</option>
              <option value="bool">Boolean</option>
            </select>
          </div>
          <div>
            <select
              value={updateMechanism}
              onChange={(e) => setUpdateMechanism(e.target.value as UpdateMechanism)}
              className="w-full px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
            >
              <option value="overwrite">Overwrite</option>
              <option value="append">Append</option>
            </select>
          </div>
          <div className="flex space-x-2">
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="flex-1 px-2 py-1 bg-zinc-700 border border-zinc-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 text-zinc-100 text-sm"
            />
            <button
              onClick={handleSave}
              className="px-2 py-1 bg-indigo-600 hover:bg-indigo-500 rounded-md text-white text-xs"
            >
              Save
            </button>
            <button
              onClick={() => setEditing(false)}
              className="px-2 py-1 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100 text-xs"
            >
              Cancel
            </button>
            <button
              onClick={() => deleteStateVariable(variable.id)}
              className="px-2 py-1 bg-red-600 hover:bg-red-500 rounded-md text-white text-xs"
            >
              Delete
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="text-zinc-300">{variable.name}</div>
          <div className="text-zinc-400">{variable.type}</div>
          <div className={`text-xs px-2 py-0.5 rounded-full ${variable.updateMechanism === 'overwrite' ? 'bg-blue-500' : 'bg-green-500'}`}>
            {variable.updateMechanism}
          </div>
          <div className="flex justify-between items-center">
            <span className="text-zinc-400 text-sm">{variable.description || '-'}</span>
            <button
              onClick={() => setEditing(true)}
              className="px-2 py-1 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-100 text-xs"
            >
              Edit
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Step3;
