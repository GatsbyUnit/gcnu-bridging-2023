import sys
import os.path
import argparse
import configparser
import numpy as np
import plotly.graph_objects as go

sys.path.append(os.path.expanduser("~/dev/research/programs/repos/python"))
import joacorapela_common.utils.probability


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_samples",
                        help="number of samples to generate", type=int,
                        default=5)
    parser.add_argument("--n_points_ellipse",
                        help="number of points to use in drawing the "
                             "confidence ellipse", type=int, default=100)
    parser.add_argument("--ellipse_quantile",
                        help="percentage of samples included in the ellipse",
                        type=float, default=0.95)
    parser.add_argument("--sigma_yx",
                        help="measurements noise standard deviation along the "
                             "x axis", type=float, default=1.0)
    parser.add_argument("--sigma_yy",
                        help="measurements noise standard deviation along the "
                             "y axis", type=float, default=1.0)
    parser.add_argument("--rho_y",
                        help="measurements noise correlation coefficient",
                        type=float, default=0.0)
    parser.add_argument("--z_info_filename", help="filename to save samples, "
                        "mean and covariance of z", type=str,
                        default="results/z_info.npz")
    parser.add_argument("--y_info_filename_pattern", help="pattern of filename "
                        "to save samples, mean and covariance of y", type=str,
                        default="results/y_info_nSamples{:05d}.npz")
    parser.add_argument("--y_metadata_filename_pattern",
                        help="pattern of filename to save metadata of y",
                        type=str, default="results/y_metadata_nSamples{:05d}.ini")
    args = parser.parse_args()

    n_samples = args.n_samples
    n_points_ellipse = args.n_points_ellipse
    ellipse_quantile = args.ellipse_quantile
    sigma_yx = args.sigma_yx
    sigma_yy = args.sigma_yy
    rho_y = args.rho_y
    z_info_filename = args.z_info_filename
    y_info_filename = args.y_info_filename_pattern.format(n_samples)
    y_metadata_filename = args.y_metadata_filename_pattern.format(n_samples)

    load_res = np.load(z_info_filename)
    samples_z = load_res["samples_z"]
    random_index = np.random.randint(low=0, high=len(samples_z), size=1).item()
    mean_y = samples_z[random_index, :]
    cov_y = np.array([[sigma_yx**2, rho_y*sigma_yx*sigma_yy],
                     [rho_y*sigma_yx*sigma_yy, sigma_yy**2]])
    samples_y = np.random.multivariate_normal(mean=mean_y, cov=cov_y,
                                              size=n_samples)

    # save y_info and metadata for next item
    np.savez(samples_y=samples_y, mean_y=mean_y, cov_y=cov_y,
             file=y_info_filename)
    metadata_config = configparser.ConfigParser()
    metadata_config["z_info"] = {"filename": z_info_filename}
    with open(y_metadata_filename, "w") as f:
        metadata_config.write(f)

    ellipse_x, ellipse_y = \
        joacorapela_common.utils.probability.quantileEllipse(
            mean=mean_y, cov=cov_y, quantile=ellipse_quantile,
            N=n_points_ellipse)

    # plot data
    fig = go.Figure()
    trace_samples = go.Scatter(x=samples_y[:, 0], y=samples_y[:, 1],
                               mode="markers", name="samples")
    trace_mean = go.Scatter(x=[mean_y[0]], y=[mean_y[1]], mode="markers",
                            name="mean")
    trace_ellipse = go.Scatter(x=ellipse_x, y=ellipse_y, mode="lines",
                               name="{:.0f}% quantile".format(
                                   ellipse_quantile*100))
    fig.add_trace(trace_samples)
    fig.add_trace(trace_mean)
    fig.add_trace(trace_ellipse)
    fig.update_layout(
        xaxis_title=r"$y_x$",
        yaxis_title=r"$y_y$",
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    fig.show()

    import pdb; pdb.set_trace()


if __name__ == "__main__":
    main(sys.argv)
