import numpy as np
import matplotlib.pyplot as plt

def calc_p_accept(m, eps, gamma, rt=1):
    """Boltzmann probability of acceptance."""
    return 1.0 / (1.0 + np.exp((-2 * gamma * m - eps) / rt))

def plot_cgt_landscapes():
    # Grid setup
    m_vals = np.arange(0, 1.01, 0.02)
    eps_vals = np.arange(-2, 3.5, 0.5)
    # Select 3 gamma values as requested
    gamma_vals = np.linspace(1, 8, 3) 

    # Create figure: 2 rows (3D + Heatmap), 3 columns (for the 3 gammas)
    fig = plt.figure(figsize=(18, 12))
    M, EPS = np.meshgrid(m_vals, eps_vals)

    for i, gamma in enumerate(gamma_vals):
        # --- Top Row: 3D Surface ---
        ax_3d = fig.add_subplot(2, 3, i + 1, projection='3d')
        Z = calc_p_accept(M, EPS, gamma)
        ax_3d.plot_surface(M, EPS, Z, cmap='viridis', alpha=0.8, edgecolor='none')
        ax_3d.set_title(f"Gamma = {gamma:.1f} (3D)")
        ax_3d.set_xlabel('m'); ax_3d.set_ylabel('eps'); ax_3d.set_zlabel('P(Accept)')
        ax_3d.view_init(elev=20, azim=135)

        # --- Bottom Row: 2D Heatmap ---
        ax_2d = fig.add_subplot(2, 3, i + 4)
        im = ax_2d.imshow(Z, origin='lower', extent=[0, 1, -2, 3], 
                          aspect='auto', cmap='viridis', vmin=0, vmax=1)
        ax_2d.set_title(f"Gamma = {gamma:.1f} (Heatmap)")
        ax_2d.set_xlabel('Offer Fraction (m)')
        ax_2d.set_ylabel('Epsilon')

    plt.colorbar(im, ax=fig.get_axes(), label='Probability of Acceptance', orientation='horizontal', pad=0.05)
    plt.suptitle("Thermodynamic Acceptance Landscapes and Heatmaps", fontsize=18)
    plt.show()

if __name__ == "__main__":
    plot_cgt_landscapes()