/**
 * @jest-environment jsdom
 */

import fs from 'fs';
import path from 'path';

const html = fs.readFileSync(path.join(process.cwd(), 'templates', 'admin', 'report.html'), 'utf8');
const bodyHTML = (html.match(/<body[^>]*>([\s\S]*)<\/body>/i)?.[1] || '').replace(/<script[^>]*>[\s\S]*?<\/script>\s*$/, '');

const reportScriptSpecifier = '../static/js/admin_report.js';

describe('Admin Report Page', () => {
    let formatCurrency;
    let renderTable;
    let loadReport;

    beforeEach(() => {
        document.body.innerHTML = bodyHTML;
        jest.clearAllMocks();
        global.fetch = jest.fn();
        window.fetch = global.fetch;

        window.localStorage.clear();
        window.localStorage.setItem('token', 'admin-token');
        global.localStorage = window.localStorage;

        const script = fs.readFileSync(path.join(process.cwd(), 'static', 'js', 'admin_report.js'), 'utf8');
        const scriptWithoutExport = script.replace(/export\s*\{[\s\S]*\};?\s*$/, '');
        const setupReportPage = new Function(scriptWithoutExport + '; return { formatCurrency, renderTable, loadReport };');
        ({ formatCurrency, renderTable, loadReport } = setupReportPage());
        window.onload = null;
    });

    test('displays 6 month columns in report table head', () => {
        const months = [
            { label: '01/2026' },
            { label: '02/2026' },
            { label: '03/2026' },
            { label: '04/2026' },
            { label: '05/2026' },
            { label: '06/2026' }
        ];

        renderTable(months, [
            {
                restaurant_name: 'Test Restaurant',
                restaurant_id: 1,
                selected_month_revenue: 1000000,
                total_6_months: 6000000,
                monthly_revenue: months.map(() => ({ revenue: 1000000 }))
            }
        ]);

        const headers = document.querySelectorAll('#report_table_head th');
        expect(headers.length).toBe(9);
        expect(Array.from(headers).slice(3).map((th) => th.textContent)).toEqual(months.map((month) => month.label));
    });

    test('formats numeric values as VNĐ currency', () => {
        expect(formatCurrency(1000000)).toBe('1.000.000đ');
        expect(formatCurrency(0)).toBe('0đ');
    });

    test('shows Loading... while loading report data', async () => {
        document.getElementById('report_month').value = '2026-06';

        global.fetch.mockResolvedValueOnce({
            status: 200,
            json: async () => ({
                status: 'success',
                total_report: 0,
                total_6_months: 0,
                restaurant_count: 0,
                months: [],
                restaurants: []
            })
        });

        const loadPromise = loadReport();

        expect(document.getElementById('status_text').textContent).toBe('Loading...');
        expect(document.getElementById('table_status').textContent).toBe('Loading...');

        await loadPromise;
    });

    test('shows Phiên làm việc hết hạn when API returns 401', async () => {
        document.getElementById('report_month').value = '2026-06';

        global.fetch.mockResolvedValueOnce({
            status: 401,
            json: async () => ({})
        });

        await loadReport();

        expect(document.getElementById('status_note').textContent).toBe('Phiên làm việc hết hạn');
    });
});
