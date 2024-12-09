# from odoo import http
# from odoo.http import request
#
# class RealEstateProjectController(http.Controller):
#
#     @http.route('/real_estate/projects', type='http', auth='public', website=True)
#     def list_projects(self, **kwargs):
#         # Fetch all projects
#         projects = request.env['real.estate.project'].search([])
#         return request.render('real_estate_project.project_list', {
#             'projects': projects,
#         })
#
#     @http.route('/real_estate/project/<int:project_id>', type='http', auth='public', website=True)
#     def view_project(self, project_id, **kwargs):
#         # Fetch a specific project by ID
#         project = request.env['real.estate.project'].browse(project_id)
#         if not project.exists():
#             return request.not_found()
#         return request.render('real_estate_project.project_detail', {
#             'project': project,
#         })
#
#     @http.route('/real_estate/project/new', type='http', auth='user', website=True)
#     def create_project(self, **kwargs):
#         # Render a form to create a new project
#         return request.render('real_estate_project.project_form', {})
#
#     @http.route('/real_estate/project/save', type='http', auth='user', website=True, methods=['POST'])
#     def save_project(self, **kwargs):
#         # Save the new project
#         project_data = {
#             'project_code': kwargs.get('project_code'),
#             'name': kwargs.get('name'),
#             'status': kwargs.get('status'),
#             'project_type': kwargs.get('project_type'),
#             'deposit_value': kwargs.get('deposit_value'),
#             'estimated_handover_date': kwargs.get('estimated_handover_date'),
#             'apartment_area': kwargs.get('apartment_area'),
#             'commercial_area': kwargs.get('commercial_area'),
#         }
#         request.env['real.estate.project'].create(project_data)
#         return request.redirect('/real_estate/projects')
