odoo.define('tamkeen_helpdesk_pro.Dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');

    var HelpdeskDashboard = AbstractAction.extend({
        template: 'HelpdeskDashboard',
        
        events: {
            'click .ticket-row': '_onTicketClick'
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._loadDashboardData();
            });
        },

        _loadDashboardData: function () {
            var self = this;
            return rpc.query({
                route: '/helpdesk/dashboard/data'
            }).then(function (data) {
                self.dashboardData = data;
                self._renderDashboard();
            });
        },

        _renderDashboard: function () {
            var self = this;
            
            // Update KPIs
            this.$('.total-tickets .value').text(this.dashboardData.kpis.total);
            this.$('.open-tickets .value').text(this.dashboardData.kpis.open);
            this.$('.closed-tickets .value').text(this.dashboardData.kpis.closed);
            this.$('.customer-rating .value').text(this.dashboardData.kpis.rating + '/5');
            
            // Update trend
            var trend = this.dashboardData.kpis.trend;
            var trendHtml = '';
            if (trend >= 0) {
                trendHtml = '<i class="fa fa-arrow-up"></i> ' + trend + '% زيادة';
            } else {
                trendHtml = '<i class="fa fa-arrow-down"></i> ' + Math.abs(trend) + '% انخفاض';
            }
            this.$('.trend').html(trendHtml);
            
            // Render charts
            this._renderLineChart();
            this._renderDoughnutChart();
            
            // Render recent tickets table
            this._renderRecentTickets();
        },

        _renderLineChart: function () {
            var ctx = this.$('#ticketsChart')[0];
            if (!ctx) return;
            
            ctx = ctx.getContext('2d');
            var labels = [];
            var newData = [];
            var closedData = [];
            
            for (var i = 0; i < this.dashboardData.weekly.length; i++) {
                labels.push(this.dashboardData.weekly[i].date);
                newData.push(this.dashboardData.weekly[i].new);
                closedData.push(this.dashboardData.weekly[i].closed);
            }
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'تذاكر جديدة',
                            data: newData,
                            borderColor: '#2563eb',
                            backgroundColor: 'rgba(37, 99, 235, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'تذاكر مغلقة',
                            data: closedData,
                            borderColor: '#10b981',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.4,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },

        _renderDoughnutChart: function () {
            var ctx = this.$('#statusChart')[0];
            if (!ctx) return;
            
            ctx = ctx.getContext('2d');
            var labels = [];
            var data = [];
            
            for (var i = 0; i < this.dashboardData.status.length; i++) {
                labels.push(this.dashboardData.status[i].name);
                data.push(this.dashboardData.status[i].count);
            }
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            '#3b82f6',
                            '#f97316',
                            '#22c55e',
                            '#8b5cf6',
                            '#ec4899'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        },

        _renderRecentTickets: function () {
            var self = this;
            var tbody = this.$('tbody');
            tbody.empty();
            
            var priorityLabels = {
                '0': 'منخفضة',
                '1': 'عادية',
                '2': 'عالية',
                '3': 'عاجلة'
            };
            
            var priorityColors = {
                '0': '#10b981',
                '1': '#64748b',
                '2': '#f59e0b',
                '3': '#ef4444'
            };
            
            for (var i = 0; i < this.dashboardData.recent.length; i++) {
                var ticket = this.dashboardData.recent[i];
                
                var priorityLabel = priorityLabels[ticket.priority] || 'عادية';
                var priorityColor = priorityColors[ticket.priority] || '#64748b';
                var statusClass = ticket.is_closed ? 'status-closed' : 'status-open';
                var statusText = ticket.stage;
                
                var row = $('<tr class="ticket-row">').attr('data-id', ticket.id);
                row.html(
                    '<td>' + ticket.number + '</td>' +
                    '<td>' + ticket.customer + '</td>' +
                    '<td>' + ticket.subject + '</td>' +
                    '<td>' + ticket.date + '</td>' +
                    '<td><span style="color: ' + priorityColor + '; font-weight: bold;">' + priorityLabel + '</span></td>' +
                    '<td><span class="status-badge ' + statusClass + '">' + statusText + '</span></td>'
                );
                tbody.append(row);
            }
        },

        _onTicketClick: function (ev) {
            var ticketId = parseInt($(ev.currentTarget).data('id'));
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'helpdesk.ticket',
                res_id: ticketId,
                views: [[false, 'form']],
                target: 'current'
            });
        }
    });

    core.action_registry.add('helpdesk_dashboard', HelpdeskDashboard);

    return HelpdeskDashboard;
});