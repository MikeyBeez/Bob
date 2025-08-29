/**
 * Job Queue Visualization Component
 * 
 * Real-time dashboard for Bob's hierarchical async job queue system.
 * Shows priority queues, active jobs, dependencies, and execution flow.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const JobQueueDashboard = () => {
  const [jobQueues, setJobQueues] = useState({
    critical: [],
    high: [],
    normal: [],
    low: []
  });
  
  const [activeJobs, setActiveJobs] = useState([]);
  const [jobStats, setJobStats] = useState({});
  const [jobDependencies, setJobDependencies] = useState([]);

  // Mock data - would come from Bob's job queue system
  useEffect(() => {
    const mockData = {
      jobQueues: {
        critical: [
          { id: 'job1', type: 'protocol_execution', name: 'error-recovery', priority: 'critical', estimated: '30s' },
          { id: 'job2', type: 'brain_operation', name: 'memory_cleanup', priority: 'critical', estimated: '15s' }
        ],
        high: [
          { id: 'job4', type: 'tool_call', name: 'cognitive_process', priority: 'high', estimated: '45s' },
          { id: 'job5', type: 'protocol_execution', name: 'user-communication', priority: 'high', estimated: '20s' }
        ],
        normal: [
          { id: 'job6', type: 'batch_operation', name: 'file_analysis', priority: 'normal', estimated: '2m' },
          { id: 'job7', type: 'tool_call', name: 'find_project', priority: 'normal', estimated: '10s' },
          { id: 'job8', type: 'tool_call', name: 'git_status', priority: 'normal', estimated: '5s' },
          { id: 'job9', type: 'tool_call', name: 'filesystem_read', priority: 'normal', estimated: '8s' }
        ],
        low: [
          { id: 'job10', type: 'tool_call', name: 'cleanup_cache', priority: 'low', estimated: '1m' },
          { id: 'job11', type: 'protocol_execution', name: 'performance_monitoring', priority: 'low', estimated: '3m' }
        ]
      },
      activeJobs: [
        { id: 'active1', type: 'protocol_execution', name: 'error-recovery', priority: 'critical', progress: 75, startTime: Date.now() - 15000 },
        { id: 'active2', type: 'tool_call', name: 'cognitive_process', priority: 'high', progress: 45, startTime: Date.now() - 8000 },
        { id: 'active3', type: 'batch_operation', name: 'file_analysis', priority: 'normal', progress: 20, startTime: Date.now() - 25000 }
      ],
      jobStats: {
        totalJobs: 45,
        completedJobs: 38,
        failedJobs: 2,
        activeJobs: 3,
        queuedJobs: 9,
        maxConcurrent: 5,
        avgProcessingTime: '1m 23s',
        successRate: 95.6
      },
      jobDependencies: [
        { from: 'job7', to: 'job8', type: 'sequential' },
        { from: 'job8', to: 'job9', type: 'sequential' },
        { from: 'job4', to: 'job6', type: 'merge' },
        { from: 'job5', to: 'job6', type: 'merge' }
      ]
    };
    
    setJobQueues(mockData.jobQueues);
    setActiveJobs(mockData.activeJobs);
    setJobStats(mockData.jobStats);
    setJobDependencies(mockData.jobDependencies);
  }, []);

  const getPriorityColor = (priority) => {
    const colors = {
      critical: 'bg-red-500',
      high: 'bg-orange-500',
      normal: 'bg-blue-500',
      low: 'bg-gray-500'
    };
    return colors[priority] || 'bg-gray-500';
  };

  const getJobTypeIcon = (type) => {
    const icons = {
      protocol_execution: '📋',
      tool_call: '🔧',
      batch_operation: '⚡',
      brain_operation: '🧠'
    };
    return icons[type] || '⚙️';
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Job Queue Control Center</h1>
          <p className="text-gray-600">Hierarchical Async Job Processing System</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Jobs</h3>
            <p className="text-2xl font-bold text-gray-900">{jobStats.totalJobs}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Success Rate</h3>
            <p className="text-2xl font-bold text-green-600">{jobStats.successRate}%</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Active Jobs</h3>
            <p className="text-2xl font-bold text-blue-600">{jobStats.activeJobs}/{jobStats.maxConcurrent}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Avg Processing</h3>
            <p className="text-2xl font-bold text-purple-600">{jobStats.avgProcessingTime}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Priority Queues */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">📋 Priority Queues</h2>
            
            {Object.entries(jobQueues).map(([priority, jobs]) => (
              <div key={priority} className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium capitalize text-gray-700">{priority} Queue</h3>
                  <span className="text-sm text-gray-500">({jobs.length} jobs)</span>
                </div>
                
                <div className="space-y-2">
                  <AnimatePresence>
                    {jobs.map((job, index) => (
                      <motion.div
                        key={job.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className="flex items-center p-3 bg-gray-50 rounded-lg border-l-4"
                        style={{ borderLeftColor: getPriorityColor(priority).replace('bg-', '') }}
                      >
                        <span className="text-lg mr-3">{getJobTypeIcon(job.type)}</span>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-gray-800">{job.name}</span>
                            <span className="text-xs text-gray-500">~{job.estimated}</span>
                          </div>
                          <div className="text-xs text-gray-600">{job.type.replace('_', ' ')}</div>
                        </div>
                        <div className="text-xs text-gray-400">#{index + 1}</div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  {jobs.length === 0 && (
                    <div className="text-center text-gray-400 py-4">No jobs in {priority} queue</div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Active Jobs */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">⚡ Active Jobs ({activeJobs.length}/{jobStats.maxConcurrent})</h2>
            
            <div className="space-y-4">
              {activeJobs.map((job) => {
                const runningTime = Math.floor((Date.now() - job.startTime) / 1000);
                return (
                  <motion.div
                    key={job.id}
                    className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border"
                    animate={{ scale: [1, 1.02, 1] }}
                    transition={{ duration: 2, repeat: Infinity, repeatType: "reverse" }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        <span className="text-lg mr-3">{getJobTypeIcon(job.type)}</span>
                        <div>
                          <div className="font-medium text-gray-800">{job.name}</div>
                          <div className="text-xs text-gray-600">{job.type} • {job.priority}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-gray-700">{job.progress}%</div>
                        <div className="text-xs text-gray-500">{runningTime}s</div>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <motion.div
                        className={`h-2 rounded-full ${getPriorityColor(job.priority)}`}
                        initial={{ width: 0 }}
                        animate={{ width: `${job.progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>

        </div>

        {/* Job Dependencies Graph */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">🔗 Job Dependencies & Workflows</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Dependency List */}
            <div>
              <h3 className="font-medium text-gray-700 mb-3">Dependency Chain</h3>
              <div className="space-y-2">
                {jobDependencies.map((dep, index) => (
                  <div key={index} className="flex items-center p-2 bg-gray-50 rounded">
                    <span className="font-mono text-sm text-blue-600">{dep.from}</span>
                    <span className="mx-2 text-gray-400">→</span>
                    <span className="font-mono text-sm text-green-600">{dep.to}</span>
                    <span className="ml-auto text-xs text-gray-500 capitalize">{dep.type}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Workflow Patterns */}
            <div>
              <h3 className="font-medium text-gray-700 mb-3">Common Patterns</h3>
              <div className="space-y-3">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <div className="font-medium text-blue-800">Sequential Processing</div>
                  <div className="text-sm text-blue-600">job7 → job8 → job9</div>
                  <div className="text-xs text-gray-600">Project analysis workflow</div>
                </div>
                
                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="font-medium text-green-800">Parallel → Merge</div>
                  <div className="text-sm text-green-600">job4, job5 → job6</div>
                  <div className="text-xs text-gray-600">Cognitive processing merge</div>
                </div>
                
                <div className="p-3 bg-purple-50 rounded-lg">
                  <div className="font-medium text-purple-800">Background Tasks</div>
                  <div className="text-sm text-purple-600">Low priority maintenance</div>
                  <div className="text-xs text-gray-600">Cleanup & monitoring</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Job Controls */}
        <div className="mt-6 flex justify-between items-center">
          <div className="flex space-x-4">
            <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
              ⏸️ Pause Queue
            </button>
            <button className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors">
              ▶️ Resume Queue
            </button>
            <button className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors">
              🔄 Restart Failed Jobs
            </button>
          </div>
          
          <div className="flex space-x-2">
            <button className="px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-sm">
              📊 Export Logs
            </button>
            <button className="px-3 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-sm">
              ⚙️ Queue Settings
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default JobQueueDashboard;
