$(document).ready(function () {
    ///////////////////////////////////////////////////////////////////////////
    // Build pi projects chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('pi_projects_chart', {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: "Principal Investigor's Projects",
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        series: [{
            type: 'pie',
            keys: ['name', 'y', 'selected', 'sliced'],
            data: [
                ['Active', 5, false],
                ['Dormant', 2, false],
                ['Inactive', 1, false],
                ['Retired', 1, false],
            ],
        }],
        exporting: {
            csv: {
                dateFormat: '%Y-%m-%d'
            }
        }
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build project users chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('project_users_chart', {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: "Users status",
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        series: [{
            type: 'pie',
            keys: ['name', 'y', 'selected', 'sliced'],
            data: [
                ['Active', 10, false],
                ['Dormant', 1, false],
                ['Inactive', 3, false],
            ],
        }],
        exporting: {
            csv: {
                dateFormat: '%Y-%m-%d'
            }
        }
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build rate of usage chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('rate_of_usage_chart_core', {
        title: {
            text: 'Rate Of Usage',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        yAxis: {
            title: {
                text: 'Unit?'
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
            title: {
                text: 'Month'
            }
        },
        series: [{
            name: 'CPU Time',
            data: [43934, 52503, 57177, 97031, 137133, 69658, 154175, 119931]
        }, {
            name: 'Wait TIme',
            data: [24916, 24064, 29742, 29851, 32490, 30282, 38121, 40434]
        }, {
            name: 'Wall Time',
            data: [11744, 17722, 16005, 19771, 20185, 24377, 32147, 39387]
        },],
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build cumlative usage chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('cumlative_usage_chart_core', {
        title: {
            text: 'Cumlative Usage',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        yAxis: {
            title: {
                text: 'Unit?'
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
            title: {
                text: 'Month'
            }
        },
        series: [{
            name: 'CPU Time',
            data: [43934, 52503, 57177, 69658, 97031, 119931, 137133, 154175]
        }, {
            name: 'Wait TIme',
            data: [24064, 24916, 29742, 29851, 30282, 32490, 38121, 40434]
        }, {
            name: 'Wall Time',
            data: [11744, 16005, 17722, 19771, 20185, 24377, 32147, 39387]
        },],
    });



    ///////////////////////////////////////////////////////////////////////////
    // Build user usage chart
    ///////////////////////////////////////////////////////////////////////////

    Highcharts.chart('user_usage_chart', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Individual User Usage',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        xAxis: {
            type: 'category'
        },
        legend: {
            enabled: true
        },
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    enabled: false,
                    style: {
                        color: 'white',
                        textShadow: '0 0 2px black, 0 0 2px black'
                    }
                },
                stacking: 'normal'
            }
        },

        series: [{
            name: 'Aaron',
            data: [{
                name: 'Jun',
                y: 6,
                drilldown: 'jun_aaron'
            }, {
                name: 'July',
                y: 8,
                drilldown: 'july_aaron'
            }]
        }, {
            name: 'Ade',
            data: [{
                name: 'Jun',
                y: 6,
                drilldown: 'jun_ade'
            }, {
                name: 'July',
                y: 3,
                drilldown: 'july_ade'
            }]
        }],
        drilldown: {
            activeDataLabelStyle: {
                color: 'white',
                textShadow: '0 0 2px black, 0 0 2px black'
            },
            series: [{
                id: 'jun_aaron',
                name: 'Jun',
                data: [
                    ['CPU Time', 3],
                    ['Wait Time', 2],
                    ['Wall Time', 1],
                ]
            }, {
                id: 'jun_ade',
                name: 'Jun',
                data: [
                    ['CPU Time', 1],
                    ['Wait Time', 2],
                    ['Wall Time', 3],
                ]
            },
            {
                id: 'july_aaron',
                name: 'July',
                data: [
                    ['CPU Time', 6],
                    ['Wait Time', 1],
                    ['Wall Time', 1],
                ]
            }, {
                id: 'july_ade',
                name: 'July',
                data: [
                    ['CPU Time', 1],
                    ['Wait Time', 1],
                    ['Wall Time', 1],
                ]
            }]
        }
    })




    ///////////////////////////////////////////////////////////////////////////
    // Build usage by partition chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('usage_by_partition_chart', {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: 'Usage by partition',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        accessibility: {
            point: {
                valueSuffix: '%'
            }
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                },
                showInLegend: true
            }
        },
        series: [{
            name: 'Paritions',
            colorByPoint: true,
            data: [{
                name: 'CF-compute',
                y: 50,
                sliced: true,
                selected: true
            }, {
                name: 'SW-gpu',
                y: 10
            }, {
                name: 'SW-compute',
                y: 10
            }, {
                name: 'CF-gpu_v100',
                y: 10
            }, {
                name: 'CF-htc',
                y: 10
            },
            {
                name: 'CF-xhtc',
                y: 10
            }]
        }],
        exporting: {
            csv: {
                dateFormat: '%Y-%m-%d'
            }
        }
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build efficiency chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('compute_efficency_chart', {
        chart: {
            type: 'spline',
        },
        title: {
            text: 'Efficency',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        xAxis: {
            type: 'datetime',
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        },
        yAxis: {
            title: {
                text: 'Efficency'
            },
            max: 100,
            minorGridLineWidth: 0,
            gridLineWidth: 0,
            alternateGridColor: null,
            plotBands: [{
                from: 0,
                to: 40,
                color: 'rgba(68, 170, 213, 0.1)',
                label: {
                    text: 'Poor',
                    style: {
                        color: '#606060'
                    }
                }
            }, {
                from: 40,
                to: 50,
                color: 'rgba(0, 0, 0, 0)',
                label: {
                    text: 'Fair',
                    style: {
                        color: '#606060'
                    }
                }
            }, {
                from: 50,
                to: 75,
                color: 'rgba(68, 170, 213, 0.1)',
                label: {
                    text: 'Good',
                    style: {
                        color: '#606060'
                    }
                }
            }, {
                from: 75,
                to: 100,
                color: 'rgba(0, 0, 0, 0)',
                label: {
                    text: 'Excellent',
                    style: {
                        color: '#606060'
                    }
                }
            }]
        },
        series: [{
            name: 'Efficency',
            data: [
                10, 20, 30, 40, 50, 60, 70
            ]
        }],
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build core count and node utilisation chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('number_of_processors_chart', {
        title: {
            text: 'Core count and node utilisation',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        },
        series: [{
            type: 'column',
            name: 'Total cores',
            data: [3, 2, 1, 3, 4]
        }, {
            type: 'spline',
            name: 'Average cores per job',
            data: [1.5, 1, .5, 1, 2.2],
            marker: {
                lineWidth: 2,
                lineColor: Highcharts.getOptions().colors[3],
                fillColor: 'white'
            }
        },],
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build jobs chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('per_job_average_chart', {
        title: {
            text: 'Per-Job average stats',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        },
        series: [{
            type: 'column',
            name: 'CPU Time',
            data: [3, 2, 1, 3, 4]
        }, {
            type: 'column',
            name: 'Wait Time',
            data: [2, 3, 5, 7, 6]
        }, {
            type: 'column',
            name: 'Wall Time',
            data: [2, 3, 5, 7, 6]
        }],
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build number or slurm jobs chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('num_slurm_jobs_chart', {
        title: {
            text: 'Number of jobs per month',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        },
        series: [{
            type: 'column',
            name: 'Number of Jobs',
            data: [3, 2, 1, 3, 4]
        }],
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build disk space storage chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('disk_space_storage_chart', {
        title: {
            text: 'Disk Space',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        },
        series: [{
            type: 'column',
            name: 'Home',
            data: [3, 2, 1, 3, 4]
        }, {
            type: 'column',
            name: 'Scratch',
            data: [2, 3, 5, 7, 6]
        }],
    });

    ///////////////////////////////////////////////////////////////////////////
    // Build file count storage chart
    ///////////////////////////////////////////////////////////////////////////
    Highcharts.chart('file_count_storage_chart', {
        title: {
            text: 'File Count',
            style: {
                color: '#5e6e82F',
                fontSize: '16px',
                fontFamily: 'Lato',
            }
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        },
        series: [{
            type: 'column',
            name: 'Home',
            data: [3, 2, 1, 3, 4]
        }, {
            type: 'column',
            name: 'Scratch',
            data: [2, 3, 5, 7, 6]
        }],
    });
});
